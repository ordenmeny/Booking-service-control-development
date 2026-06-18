from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.helper import sessionmanager

SessionDep = Annotated[
    AsyncSession,
    Depends(sessionmanager.get_session),
]
