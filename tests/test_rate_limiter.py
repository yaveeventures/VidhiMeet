import pytest
from backend.rate_limiter import rate_limiter
from backend.config import get_settings

settings = get_settings()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    # Clear internal rate limiter state before each test
    with rate_limiter._lock:
        rate_limiter._requests.clear()
        rate_limiter._violations.clear()
        rate_limiter._auth_attempts.clear()
        rate_limiter._blocked_ips.clear()
    settings.rate_limit_enabled = True
    yield
    with rate_limiter._lock:
        rate_limiter._requests.clear()
        rate_limiter._violations.clear()
        rate_limiter._auth_attempts.clear()
        rate_limiter._blocked_ips.clear()


def test_auth_rate_limiting(client):
    """Verify that requests exceeding the auth limit return HTTP 429 with Retry-After header."""
    # 10 requests allowed
    for i in range(10):
        resp = client.post("/api/v1/auth/login", json={
            "email": f"user{i}@example.com",
            "password": "wrong-password"
        })
        assert resp.status_code == 401

    # 11th request triggers HTTP 429 Too Many Requests
    resp_overflow = client.post("/api/v1/auth/login", json={
        "email": "user11@example.com",
        "password": "wrong-password"
    })
    assert resp_overflow.status_code == 429
    assert "Retry-After" in resp_overflow.headers
    assert "X-RateLimit-Limit" in resp_overflow.headers
    assert resp_overflow.headers["X-RateLimit-Limit"] == "10"


def test_auth_exponential_backoff(client):
    """Verify per-account and per-IP exponential backoff triggers after max free attempts."""
    target_email = "backoff_user@example.com"
    # Make 5 attempts (rate_limit_auth_account_max_attempts = 5)
    for _ in range(5):
        resp = client.post("/api/v1/auth/login", json={"email": target_email, "password": "wrong-password"})
        assert resp.status_code == 401

    # 6th attempt should trigger 429 exponential backoff with Retry-After
    resp_backoff = client.post("/api/v1/auth/login", json={"email": target_email, "password": "wrong-password"})
    assert resp_backoff.status_code == 429
    assert "backoff" in resp_backoff.json()["detail"].lower()
    assert "Retry-After" in resp_backoff.headers


def test_configurable_tier_thresholds(client):
    """Verify that rate limit tier thresholds are dynamically configurable via Settings."""
    orig_public_limit = settings.rate_limit_public_per_min
    try:
        # Lower public limit to 3 for testing
        settings.rate_limit_public_per_min = 3
        for _ in range(3):
            resp = client.get("/api/v1/public/stats")
            assert resp.status_code == 200

        # 4th request triggers 429
        resp_overflow = client.get("/api/v1/public/stats")
        assert resp_overflow.status_code == 429
    finally:
        settings.rate_limit_public_per_min = orig_public_limit


def test_ip_abuse_lockout(client):
    """Verify that 5 rate limit violations trigger a 15-minute 403 IP block."""
    for v in range(5):
        for i in range(10):
            client.post("/api/v1/auth/login", json={"email": f"u{i}@test.com", "password": "pwd"})
        resp = client.post("/api/v1/auth/login", json={"email": "overflow@test.com", "password": "pwd"})
        assert resp.status_code in (429, 403)

    blocked_resp = client.get("/api/v1/health")
    assert blocked_resp.status_code == 403
    assert "blocked" in blocked_resp.json()["detail"].lower()


def test_disabled_rate_limiter_setting(client):
    """Verify that disabling rate_limit_enabled setting allows requests without limits."""
    settings.rate_limit_enabled = False
    for i in range(15):
        resp = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "pwd"
        })
        assert resp.status_code == 401
