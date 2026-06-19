from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.helper import async_session_manager, sync_sessionmanager

AsyncSessionDep = Annotated[
    AsyncSession,
    Depends(async_session_manager.get_session),
]

SyncSessionDep = Annotated[
    Session,
    Depends(sync_sessionmanager.get_session),
]
