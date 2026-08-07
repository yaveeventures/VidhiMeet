import json
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import get_settings

settings = get_settings()

def safe_json_deserializer(s):
    if not s:
        return None
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return s

# --- Synchronous Engine & Session (for migrations, CLI scripts, backward compatibility) ---
raw_url = settings.database_url
if raw_url.startswith("postgresql://"):
    sync_db_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    sync_db_url = raw_url

connect_args = {"check_same_thread": False} if sync_db_url.startswith("sqlite") else {}
engine = create_engine(
    sync_db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
    json_deserializer=safe_json_deserializer
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# --- Asynchronous Engine & Session (for FastAPI async route handlers) ---
if sync_db_url.startswith("sqlite:///"):
    async_db_url = sync_db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_db_url = sync_db_url

async_connect_args = {"check_same_thread": False} if "sqlite" in async_db_url else {}
async_engine = create_async_engine(
    async_db_url,
    pool_pre_ping=True,
    connect_args=async_connect_args,
    json_deserializer=safe_json_deserializer
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
