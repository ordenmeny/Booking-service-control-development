from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


class SessionManager:
    def __init__(self, db_url: str, echo: bool):
        self.db_url = db_url
        self.engine = create_async_engine(
            self.db_url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            authocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        if not self.session_factory:
            raise RuntimeError("DB session factory is not initialized")

        async with self.session_factory() as session:
            yield session


sessionmanager = SessionManager(
    db_url=settings.db_url,
    echo=settings.ECHO,
)
