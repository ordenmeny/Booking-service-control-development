from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


class AsyncSessionManager:
    def __init__(self, db_url: str, echo: bool):
        self.engine = create_async_engine(
            db_url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        if not self.session_factory:
            raise RuntimeError("DB session factory is not initialized")

        async with self.session_factory() as session:
            yield session


class SyncSessionManager:
    def __init__(self, db_url: str, echo: bool):
        self.engine = create_engine(
            db_url,
            echo=echo,
            pool_size=10,
            max_overflow=20,
        )
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=Session,
        )

    def get_session(self):
        if not self.session_factory:
            raise RuntimeError("DB session factory is not initialized")
        return self.session_factory()


sync_sessionmanager = SyncSessionManager(
    db_url=settings.sync_db_url,
    echo=settings.ECHO,
)


async_session_manager = AsyncSessionManager(
    db_url=settings.async_db_url,
    echo=settings.ECHO,
)
