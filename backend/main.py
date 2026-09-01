import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

from .config import get_settings
from .db import Base, engine, async_engine
from .logging_config import setup_logging
from .rate_limiter import rate_limiter
from .routers import admin, auth, bank_accounts, bookings, calendar, drafting, events, lawyers, public, webhooks, websocket_chat

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import structlog

log = structlog.get_logger("main")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured telemetry logging
    setup_logging(settings.production)

    Base.metadata.create_all(engine)

    # ── Auto-migrate missing columns for existing tables ─────────────────────
    try:
        from sqlalchemy import text
        from .db import SessionLocal
        with SessionLocal() as session:
            is_sqlite = engine.dialect.name == "sqlite"
            cols = [
                ("bar_license_verified", "BOOLEAN DEFAULT FALSE"),
                ("aadhaar_verified", "BOOLEAN DEFAULT FALSE")
            ]
            for col_name, col_def in cols:
                try:
                    if is_sqlite:
                        session.execute(text(f"ALTER TABLE lawyer_profiles ADD COLUMN {col_name} {col_def};"))
                    else:
                        session.execute(text(f"ALTER TABLE lawyer_profiles ADD COLUMN IF NOT EXISTS {col_name} {col_def};"))
                    session.commit()
                except Exception as col_err:
                    session.rollback()
    except Exception as exc:
        log.info("Table migration notice", error=str(exc))

    # Ensure default admin accounts exist
    try:
        from sqlalchemy import select
        from .models import User, Role
        from .security import hash_password
        from .db import SessionLocal
        with SessionLocal() as session:
            admin_exists = session.scalar(select(User).where(User.role == Role.ADMIN))
            if not admin_exists:
                default_password_hash = hash_password("ChangeMe-Immediately-123!")
                session.add(User(
                    email="admin@vidhimeet.com",
                    full_name="VidhiMeet Admin",
                    role=Role.ADMIN,
                    password_hash=default_password_hash
                ))
                session.add(User(
                    email="surajgundi1@gmail.com",
                    full_name="Suraj Gundi",
                    role=Role.ADMIN,
                    password_hash=default_password_hash
                ))
                session.commit()
                log.info("Initial admin accounts provisioned successfully")
    except Exception as exc:
        log.error("Failed to seed initial admin user", error=str(exc))

    # Initialize Redis rate limiter if configured
    await rate_limiter.init_redis()

    # ── NTP clock synchronization (CERT-In / DPDP forensic timestamp compliance) ─
    if settings.ntp_sync_on_startup:
        try:
            from .ntp_time import check_clock_drift
            status = check_clock_drift()
            if status["within_tolerance"]:
                log.info(
                    "NTP startup check succeeded",
                    server=status["ntp_server"],
                    drift_seconds=status["drift_seconds"],
                    synced_at=status["synced_at"],
                )
            else:
                log.critical(
                    "NTP startup drift alert: Timestamps may not be forensically authoritative",
                    server=status["ntp_server"],
                    drift_seconds=status["drift_seconds"],
                )
        except (OSError, RuntimeError, KeyError, ValueError) as exc:  # pragma: no cover
            log.error("NTP startup check raised an error", error=str(exc))

    yield

    # Clean shutdown of async database engine pool
    await async_engine.dispose()

app = FastAPI(
    title="VidhiMeet API",
    version="1.0.0",
    docs_url=None if settings.production else "/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_origin_regex=None if settings.production else r"https://.*\.ngrok-free\.dev|https://.*\.ngrok\.app|https://.*\.ngrok\.io",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.middleware("http")
async def security_headers_and_rate_limit(request: Request, call_next):
    request_id = request.headers.get("x-request-id", secrets.token_hex(12))
    request.state.request_id = request_id

    # Bypass rate limiting and custom checks for CORS OPTIONS preflights
    if request.method == "OPTIONS":
        return await call_next(request)

    # Tiered rate limiting and IP abuse check
    path = request.url.path
    category = "global"
    if path.startswith("/api/v1/auth"):
        category = "auth"
    elif path.startswith("/api/v1/public") or path == "/api/v1/lawyers" or path == "/api/v1/health":
        category = "public"
    elif path.startswith("/api/v1/admin"):
        category = "admin"
    elif "authorization" in request.headers or "Authorization" in request.headers:
        category = "authenticated"

    try:
        await rate_limiter.check_async(request, category)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "detail": exc.detail, "message": exc.detail, "request_id": request_id},
            headers=exc.headers or {}
        )

    response = await call_next(request)
    daily_url = "https://*.daily.co"
    daily_wss = "wss://*.daily.co"
    response.headers.update({
        "X-Request-ID": request_id,
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        "Permissions-Policy": f'camera=(self "{daily_url}" "https://meet.jit.si" "https://8x8.vc"), microphone=(self "{daily_url}" "https://meet.jit.si" "https://8x8.vc"), display-capture=(self "{daily_url}" "https://meet.jit.si" "https://8x8.vc"), geolocation=()',
        "Content-Security-Policy": f"default-src 'self'; script-src 'self' 'unsafe-eval' https://www.gstatic.com https://www.google.com https://cdnjs.cloudflare.com https://meet.jit.si https://8x8.vc; frame-src {daily_url} https://daily.co https://meet.jit.si https://*.meet.jit.si https://8x8.vc https://*.8x8.vc https://VidhiMeet.firebaseapp.com https://www.google.com; connect-src 'self' {daily_url} {daily_wss} https://api.daily.co https://meet.jit.si https://*.meet.jit.si https://8x8.vc https://*.8x8.vc wss://*.meet.jit.si wss://*.8x8.vc https://*.googleapis.com; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src https://fonts.gstatic.com; img-src 'self' data: https:; media-src *; object-src 'none'; base-uri 'self'; worker-src blob: https://cdnjs.cloudflare.com;",
    })
    return response

# ── Two-Layer Exception Handlers ──────────────────────────────────────────────

def _cors_response(response: JSONResponse, request: Request) -> JSONResponse:
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.exception_handler(HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Standardized HTTP Exception Handler:
    - Private Layer: Log operational client errors (4xx).
    - Public Layer: Return sanitized JSON message with status code and request ID.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    log.warning(
        "HTTP_EXCEPTION | status=%d request_id=%s path=%s method=%s detail=%s",
        exc.status_code, request_id, request.url.path, request.method, exc.detail
    )
    res = JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail if isinstance(exc.detail, (str, dict, list)) else str(exc.detail),
            "message": exc.detail if isinstance(exc.detail, (str, dict, list)) else str(exc.detail),
            "request_id": request_id
        },
        headers=getattr(exc, "headers", None) or {}
    )
    return _cors_response(res, request)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Validation Exception Handler:
    - Private Layer: Log detailed field errors to server console/logs.
    - Public Layer: Return structured clean error list to client.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    log.warning(
        "VALIDATION_ERROR | request_id=%s path=%s method=%s errors=%s",
        request_id, request.url.path, request.method, exc.errors()
    )
    clean_errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", []) if str(x) != "body"])
        clean_errors.append({"field": loc or "payload", "message": err.get("msg", "Invalid value")})

    res = JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Invalid request parameter(s)",
            "errors": clean_errors,
            "request_id": request_id
        }
    )
    return _cors_response(res, request)

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """
    Database Integrity Exception Handler:
    - Private Layer: Log full database error & stack trace internally.
    - Public Layer: Return sanitized error message without exposing SQL/table details.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    log.error(
        "DATABASE_INTEGRITY_ERROR | request_id=%s path=%s method=%s exc=%s",
        request_id, request.url.path, request.method, exc, exc_info=exc
    )
    res = JSONResponse(
        status_code=409,
        content={
            "status": "error",
            "message": "The requested resource or time slot is conflicting or unavailable.",
            "request_id": request_id
        }
    )
    return _cors_response(res, request)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Global Fallback Exception Handler for unexpected server failures (500):
    - Private Layer: Log full traceback, exception type, and request context privately.
    - Public Layer: Return clean generic error message with reference request_id.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    log.error(
        "UNHANDLED_EXCEPTION | request_id=%s path=%s method=%s exc_type=%s exc=%s",
        request_id, request.url.path, request.method, type(exc).__name__, str(exc).encode("ascii", "backslashreplace").decode("ascii"), exc_info=exc
    )
    res = JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected server error occurred. Please try again later.",
            "request_id": request_id
        }
    )
    return _cors_response(res, request)

@app.get("/metrics", include_in_schema=False)
async def metrics():
    from fastapi.responses import PlainTextResponse
    import time
    uptime = time.time() - getattr(app.state, "start_time", time.time())
    body = f"""# HELP process_uptime_seconds Total process uptime in seconds
# TYPE process_uptime_seconds counter
process_uptime_seconds {uptime:.2f}
# HELP VidhiMeet_api_status API operational status (1 = healthy)
# TYPE VidhiMeet_api_status gauge
VidhiMeet_api_status 1
"""
    return PlainTextResponse(body, media_type="text/plain")

# ── Include routers ───────────────────────────────────────────────────────────
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(lawyers.router)
app.include_router(bank_accounts.router)
app.include_router(bookings.router)
app.include_router(calendar.router)
app.include_router(drafting.router)
app.include_router(webhooks.router)
app.include_router(events.router)
app.include_router(websocket_chat.router)
app.include_router(admin.router)

# ── Serve frontend static files ───────────────────────────────────────────────
class FrontendStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        full_path = scope.get("path", "")
        if full_path.startswith("/api/") or path.startswith("api/"):
            raise StarletteHTTPException(status_code=404, detail="Not Found")
        return await super().get_response(path, scope)

app.mount("/", FrontendStaticFiles(directory="frontend", html=True), name="frontend")
