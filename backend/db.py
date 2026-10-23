import json
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool, AsyncAdaptedQueuePool
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

is_pooler = "pooler.supabase.com" in sync_db_url or ":6543" in sync_db_url
is_postgres = sync_db_url.startswith("postgresql")

# In production, ensure TLS encryption (sslmode=require) is enforced if not explicitly specified
if is_postgres and settings.db_ssl_require and settings.production and "sslmode=" not in sync_db_url.lower():
    delimiter = "&" if "?" in sync_db_url else "?"
    sync_db_url = f"{sync_db_url}{delimiter}sslmode=require"

connect_args = (
    {"check_same_thread": False, "timeout": 30}
    if sync_db_url.startswith("sqlite")
    else ({"prepare_threshold": None} if is_pooler else {"options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000"})
)

# Pool configuration for synchronous engine
if sync_db_url.startswith("sqlite"):
    sync_pool_kwargs = {}
elif is_pooler:
    # Transaction poolers (PgBouncer/Supavisor) manage their own pooling; avoid client-side connection retention
    sync_pool_kwargs = {"poolclass": NullPool}
else:
    sync_pool_kwargs = {
        "poolclass": QueuePool,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_recycle": settings.db_pool_recycle_seconds,
        "pool_timeout": settings.db_pool_timeout_seconds,
    }

engine = create_engine(
    sync_db_url,
    pool_pre_ping=settings.db_pool_pre_ping,
    connect_args=connect_args,
    json_deserializer=safe_json_deserializer,
    **sync_pool_kwargs
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# --- Asynchronous Engine & Session (for FastAPI async route handlers) ---
if sync_db_url.startswith("sqlite:///"):
    async_db_url = sync_db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_db_url = sync_db_url

async_connect_args = (
    {"check_same_thread": False, "timeout": 30}
    if "sqlite" in async_db_url
    else ({"prepare_threshold": None} if is_pooler else {"options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000"})
)

# Pool configuration for asynchronous engine
if async_db_url.startswith("sqlite"):
    async_pool_kwargs = {}
elif is_pooler:
    async_pool_kwargs = {"poolclass": NullPool}
else:
    async_pool_kwargs = {
        "poolclass": AsyncAdaptedQueuePool,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_recycle": settings.db_pool_recycle_seconds,
        "pool_timeout": settings.db_pool_timeout_seconds,
    }

async_engine = create_async_engine(
    async_db_url,
    pool_pre_ping=settings.db_pool_pre_ping,
    connect_args=async_connect_args,
    json_deserializer=safe_json_deserializer,
    **async_pool_kwargs
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
