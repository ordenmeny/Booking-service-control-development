from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from app.api.models import Booking, StatusEnum


def booking_payload(**overrides):
    payload = {
        "name": "Ivan",
        "datetime": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "service_type": "massage",
    }
    payload.update(overrides)
    return payload


@pytest.mark.anyio
async def test_create_booking_returns_pending_and_queues_worker(client, db_session):
    with patch("app.api.v1.routes.booking.confirm_booking.delay") as delay_mock:
        response = await client.post(
            "/api/v1/booking/bookings",
            json=booking_payload(),
        )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Ivan"
    assert data["service_type"] == "massage"
    assert data["status"] == "pending"
    assert isinstance(data["id"], int)

    delay_mock.assert_called_once_with(data["id"])


@pytest.mark.anyio
async def test_create_booking_requires_service_type(client, db_session):
    payload = booking_payload()
    payload.pop("service_type")

    response = await client.post("/api/v1/booking/bookings", json=payload)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_booking(client, db_session):
    booking = Booking(
        name="Test",
        datetime=datetime.now(UTC),
        service_type="doctor",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    response = await client.get(f"/api/v1/booking/bookings/{booking.id}")

    assert response.status_code == 200
    assert response.json()["id"] == booking.id


@pytest.mark.anyio
async def test_get_booking_not_found(client, db_session):
    response = await client.get("/api/v1/booking/bookings/999999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_bookings_filters_by_status_and_paginates(client, db_session):
    bookings = [
        Booking(name="Pending 1", datetime=datetime.now(UTC), service_type="test"),
        Booking(name="Pending 2", datetime=datetime.now(UTC), service_type="test"),
        Booking(name="Pending 3", datetime=datetime.now(UTC), service_type="test"),
        Booking(
            name="Confirmed",
            datetime=datetime.now(UTC),
            service_type="test",
            status=StatusEnum.CONFIRMED,
        ),
    ]
    db_session.add_all(bookings)
    db_session.commit()

    response = await client.get(
        "/api/v1/booking/bookings",
        params={"status": "pending", "skip": 1, "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["skip"] == 1
    assert body["limit"] == 2
    assert len(body["items"]) == 2
    assert all(item["status"] == "pending" for item in body["items"])


@pytest.mark.anyio
async def test_list_bookings_rejects_invalid_limit(client, db_session):
    response = await client.get(
        "/api/v1/booking/bookings",
        params={"status": "pending", "limit": 101},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_list_bookings_rejects_invalid_status(client, db_session):
    response = await client.get(
        "/api/v1/booking/bookings",
        params={"status": "unknown"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_delete_pending_booking(client, db_session):
    booking = Booking(
        name="Delete",
        datetime=datetime.now(UTC),
        service_type="test",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    booking_id = booking.id

    response = await client.delete(f"/api/v1/booking/bookings/{booking_id}")

    assert response.status_code == 200
    assert response.json() == "deleted"

    db_session.expire_all()
    assert db_session.get(Booking, booking_id) is None


@pytest.mark.anyio
async def test_delete_confirmed_booking_is_forbidden(client, db_session):
    booking = Booking(
        name="Delete",
        datetime=datetime.now(UTC),
        service_type="test",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    response = await client.delete(f"/api/v1/booking/bookings/{booking.id}")

    assert response.status_code == 403
    assert db_session.get(Booking, booking.id) is not None
