import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-that-is-at-least-thirty-two-characters"

from backend.config import get_settings
get_settings.cache_clear()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pytest
import backend.db as db_module
from backend.db import Base, get_db
from backend.main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

# Point module engine and SessionLocal to in-memory test engine for threads & direct SessionLocal calls
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from backend.rate_limiter import rate_limiter
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
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
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
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
