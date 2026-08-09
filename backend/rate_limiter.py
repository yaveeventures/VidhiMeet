import time
import structlog
import json
from collections import defaultdict
from threading import Lock
from fastapi import HTTPException, Request, status
from .config import get_settings

try:
    from redis.exceptions import RedisError
except ImportError:
    class RedisError(Exception):  # type: ignore[no-redef]
        pass

log = structlog.get_logger("rate_limiter")


class SlidingWindowRateLimiter:
    def __init__(self):
        self._lock = Lock()
        self._requests = defaultdict(list)
        self._violations = defaultdict(list)
        self._auth_attempts = defaultdict(list)
        self._blocked_ips = {}  # ip -> block_until_timestamp
        self._redis_client = None

    @property
    def redis(self):
        return self._redis_client

    async def init_redis(self):
        s = get_settings()
        if s.redis_url:
            try:
                import redis.asyncio as redis
                self._redis_client = redis.from_url(s.redis_url, decode_responses=True)
                await self._redis_client.ping()
                log.info("Redis rate limiter connected successfully")
            except (ImportError, RuntimeError, OSError, RedisError) as e:
                log.warning("Redis connection failed for rate limiter, falling back to in-memory", error=str(e))
                self._redis_client = None

    def _get_tier_limit(self, category: str) -> int:
        s = get_settings()
        limits = {
            "auth": s.rate_limit_auth_per_min,
            "public": s.rate_limit_public_per_min,
            "authenticated": s.rate_limit_authenticated_per_min,
            "admin": s.rate_limit_admin_per_min,
            "uploads": s.rate_limit_uploads_per_min,
            "strict": s.rate_limit_strict_per_min,
            "global": s.rate_limit_global_per_min,
        }
        return limits.get(category, s.rate_limit_global_per_min)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "127.0.0.1"

    async def _extract_account_id(self, request: Request) -> str | None:
        account = request.query_params.get("email") or request.query_params.get("username")
        if not account and request.headers.get("content-type", "").startswith("application/json"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    data = json.loads(body_bytes)
                    if isinstance(data, dict):
                        account = data.get("email") or data.get("username") or data.get("account")
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError):
                pass
        return str(account).lower().strip() if account else None

    async def check_async(self, request: Request, category: str = "global"):
        s = get_settings()
        if not s.rate_limit_enabled:
            return

        if getattr(request.state, "_rate_limit_checked", False):
            return
        request.state._rate_limit_checked = True

        client_ip = self._get_client_ip(request)
        limit = self._get_tier_limit(category)

        # Attempt Redis check if client initialized
        if self._redis_client:
            try:
                blocked_key = f"blocked_ip:{client_ip}"
                is_blocked = await self._redis_client.get(blocked_key)
                if is_blocked:
                    ttl = await self._redis_client.ttl(blocked_key)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"IP address blocked for {ttl} seconds due to excessive automated requests.",
                        headers={"Retry-After": str(ttl)}
                    )

                key = f"ratelimit:{category}:{client_ip}"
                now = time.time()
                window_start = now - 60.0

                pipe = self._redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, 60)
                results = await pipe.execute()

                count = results[2]
                if count > limit:
                    violation_key = f"violations:{client_ip}"
                    v_count = await self._redis_client.incr(violation_key)
                    if v_count == 1:
                        await self._redis_client.expire(violation_key, 600)

                    if v_count >= 5:
                        await self._redis_client.setex(blocked_key, 900, "1")
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="IP address blocked for 15 minutes due to excessive automated requests.",
                            headers={"Retry-After": "900"}
                        )

                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded for category '{category}'. Maximum allowed: {limit} requests per minute.",
                        headers={"Retry-After": "60", "X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0"}
                    )
                return
            except HTTPException:
                raise
            except (AttributeError, RuntimeError, OSError, RedisError) as exc:
                log.warning("Redis rate limiter error, using in-memory fallback", error=str(exc))

        # In-memory fallback
        account_id = None
        if category == "auth":
            account_id = await self._extract_account_id(request)
        self.check(request, category, account_id=account_id)

    def check(self, request: Request, category: str = "global", account_id: str | None = None):
        s = get_settings()
        if not s.rate_limit_enabled:
            return

        client_ip = self._get_client_ip(request)
        now = time.time()

        with self._lock:
            # 1. Check if IP is currently blocked due to repeated abuse violations
            block_until = self._blocked_ips.get(client_ip)
            if block_until:
                if now < block_until:
                    retry_after = int(block_until - now)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"IP address blocked for {retry_after} seconds due to excessive automated requests.",
                        headers={"Retry-After": str(retry_after)}
                    )
                else:
                    del self._blocked_ips[client_ip]

            # 2. Auth Category: Per-Account & Per-IP Exponential Backoff
            if category == "auth":
                auth_window_start = now - s.rate_limit_auth_window_seconds
                track_key = f"acct:{account_id}" if account_id else f"ip:{client_ip}"
                attempts = [t for t in self._auth_attempts[track_key] if t > auth_window_start]
                self._auth_attempts[track_key] = attempts
                n_attempts = len(attempts)

                if n_attempts >= s.rate_limit_auth_account_max_attempts:
                    exponent = n_attempts - s.rate_limit_auth_account_max_attempts + 1
                    backoff = min(s.rate_limit_auth_backoff_max_seconds,
                                  s.rate_limit_auth_backoff_base_seconds * (2 ** (exponent - 1)))
                    last_attempt = attempts[-1]
                    time_since_last = now - last_attempt
                    if time_since_last < backoff:
                        needed_wait = int(backoff - time_since_last) + 1
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Exponential backoff active. Please wait {needed_wait} seconds before trying again.",
                            headers={"Retry-After": str(needed_wait)}
                        )

            # 3. Sliding Window Rate Limit Check
            limit = self._get_tier_limit(category)
            window_start = now - 60.0
            history_key = (category, client_ip)

            # Prune old request timestamps
            self._requests[history_key] = [t for t in self._requests[history_key] if t > window_start]
            recent_requests = len(self._requests[history_key])

            if recent_requests >= limit:
                # Track abuse violation
                violation_window_start = now - 600.0  # 10 minutes
                self._violations[client_ip] = [t for t in self._violations[client_ip] if t > violation_window_start]
                self._violations[client_ip].append(now)

                # If IP breaches rate limits >= 5 times in 10 minutes, block for 15 minutes
                if len(self._violations[client_ip]) >= 5:
                    self._blocked_ips[client_ip] = now + 900.0  # 15 minutes block
                    retry_after = 900
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="IP address blocked for 15 minutes due to excessive automated requests.",
                        headers={"Retry-After": str(retry_after)}
                    )

                # Standard 429 Too Many Requests
                oldest_in_window = self._requests[history_key][0]
                retry_after = max(1, int(60.0 - (now - oldest_in_window)))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for category '{category}'. Maximum allowed: {limit} requests per minute.",
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(now + retry_after))
                    }
                )

            # Record current request timestamp
            self._requests[history_key].append(now)
            if category == "auth":
                track_key = f"acct:{account_id}" if account_id else f"ip:{client_ip}"
                self._auth_attempts[track_key].append(now)


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter()


def rate_limit_dependency(category: str = "global"):
    async def dependency(request: Request):
        await rate_limiter.check_async(request, category)
    return dependency
