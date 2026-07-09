from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config.settings import settings

# Create sync engine for migrations and admin tasks
sync_database_url = settings.database_url.replace("+aiosqlite", "").replace("+asyncpg", "").replace("+aiomysql", "")
engine = create_engine(sync_database_url)

# Create sync sessionmaker (for migrations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


# Dependency to get database session
from typing import AsyncGenerator

async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Function to create all tables (for development)
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Function to close database connections
async def close_db_connections():
    await async_engine.dispose()

# sync get_db
def get_db():
    with SessionLocal() as db:
        yield db
