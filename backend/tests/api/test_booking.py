from datetime import datetime, timedelta

import pytest

from app.api.models import Booking, StatusEnum
from app.db.helper import sync_sessionmanager


@pytest.mark.anyio
async def test_create_booking(client):
    response = await client.post(
        "/api/v1/booking/bookings",
        json={
            "name": "Ivan",
            "datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "service_type": "massage",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Ivan"
    assert data["service_type"] == "massage"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.anyio
async def test_get_booking(client):
    session = sync_sessionmanager.get_session()

    booking = Booking(
        name="Test",
        datetime=datetime.utcnow(),
        service_type="doctor",
    )

    session.add(booking)
    session.commit()
    session.refresh(booking)

    response = await client.get(f"/api/v1/booking/bookings/{booking.id}")

    assert response.status_code == 200
    assert response.json()["id"] == booking.id

    session.delete(booking)
    session.commit()
    session.close()


@pytest.mark.anyio
async def test_get_booking_not_found(client):
    response = await client.get("/api/v1/booking/bookings/999999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_booking(client):
    response = await client.get(
        "/api/v1/booking/bookings",
        params={
            "status": "pending",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert "total" in body
    assert body["skip"] == 0
    assert body["limit"] == 10


@pytest.mark.anyio
async def test_list_booking_invalid_limit(client):
    response = await client.get(
        "/api/v1/booking/bookings",
        params={
            "status": "pending",
            "limit": 101,
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_delete_pending_booking(client):
    session = sync_sessionmanager.get_session()

    booking = Booking(
        name="Delete",
        datetime=datetime.utcnow(),
        service_type="test",
    )

    session.add(booking)
    session.commit()
    session.refresh(booking)

    response = await client.delete(f"/api/v1/booking/bookings/{booking.id}")

    assert response.status_code == 200
    assert response.json() == "deleted"

    session.close()


@pytest.mark.anyio
async def test_delete_confirmed_booking(client):
    session = sync_sessionmanager.get_session()

    booking = Booking(
        name="Delete",
        datetime=datetime.utcnow(),
        service_type="test",
        status=StatusEnum.CONFIRMED,
    )

    session.add(booking)
    session.commit()
    session.refresh(booking)

    response = await client.delete(f"/api/v1/booking/bookings/{booking.id}")

    assert response.status_code == 403

    session.delete(booking)
    session.commit()
    session.close()
