from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from bot.core.config import settings
from database.base import Base


async_database_url = settings.DATABASE_URL.replace(
    "sqlite://",
    "sqlite+aiosqlite://"
)

engine = create_async_engine(
    async_database_url,
    echo=False,
    connect_args={"check_same_thread": False}
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """
    Асинхронно инициализирует базу данных.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncSession:
    """
    Dependency для получения асинхронной сессии.
    """
    async with AsyncSessionLocal() as session:
        yield session
