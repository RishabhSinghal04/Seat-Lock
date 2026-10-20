import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.core.config import Config, get_config

logger: logging.Logger = logging.getLogger(__name__)
config: Config = get_config()


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    def initialize(self, url: str, echo: bool = False) -> None:
        logger.debug("initializing database engine")
        self._engine = create_async_engine(url=url, echo=echo, pool_pre_ping=True)
        self._session_maker = async_sessionmaker(
            bind=self._engine, autoflush=False, expire_on_commit=False
        )

    async def dispose(self) -> None:
        if self._engine is None:
            return
        logger.debug("disposing database engine")
        await self._engine.dispose()
        self._engine = None
        self._session_maker = None

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("database engine not initialized")
        logger.debug("initiating a database session")
        try:
            async with self._session_maker() as db:
                yield db
        finally:
            logger.debug("closing the database session")


db_manager = DatabaseSessionManager()


def init_engine() -> None:
    db_manager.initialize(url=config.DATABASE_URL, echo=config.DEBUG)


async def dispose_engine() -> None:
    await db_manager.dispose()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with db_manager.get_session() as db:
        yield db
