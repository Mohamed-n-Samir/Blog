from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config.settings import settings

# Create sync engine for migrations and admin tasks
sync_database_url = settings.database_url.replace("+aiosqlite", "").replace("+asyncpg", "").replace("+aiomysql", "")
engine = create_engine(sync_database_url)

# Create sync sessionmaker (for migrations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db

