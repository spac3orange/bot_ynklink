from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database
from environs import Env

env = Env()

# Стартовая база
DATABASE_URL = env('DB_PATH')

database = Database(DATABASE_URL)
Base = declarative_base()

engine = create_async_engine(DATABASE_URL, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)