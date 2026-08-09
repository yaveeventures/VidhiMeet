import os
os.environ["DATABASE_URL"] = "sqlite:///./test_lexconnect.db"
os.environ["JWT_SECRET"] = "test-secret-that-is-at-least-thirty-two-characters"

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pytest
from backend.db import Base, SessionLocal, engine, get_db
from backend.main import app

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from backend.rate_limiter import rate_limiter
    from backend.config import get_settings
    settings = get_settings()
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

@pytest.fixture(autouse=True)
def database():
    engine.dispose()
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    def _override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield db
    finally:
        app.dependency_overrides.clear()
        db.close()
        engine.dispose()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
