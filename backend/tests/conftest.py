import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.models import Booking
from app.api.rate_limit import reset_rate_limit
from app.db.helper import sync_sessionmanager
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_limiter():
    reset_rate_limit()
    yield
    reset_rate_limit()


@pytest.fixture
def db_session():
    session = sync_sessionmanager.get_session()
    session.execute(delete(Booking))
    session.commit()

    try:
        yield session
    finally:
        session.rollback()
        session.execute(delete(Booking))
        session.commit()
        session.close()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
