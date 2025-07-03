from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database
from app.core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=0
)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

database = Database(DATABASE_URL, min_size=1, max_size=10)

Base = declarative_base() 