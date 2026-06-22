from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from celery.exceptions import Retry

from app.api.models import Booking, StatusEnum
from app.celery_app.tasks import confirm_booking


def create_booking(db_session, **overrides):
    booking = Booking(
        name=overrides.pop("name", "Worker"),
        datetime=overrides.pop("datetime", datetime.now(UTC)),
        service_type=overrides.pop("service_type", "test"),
        **overrides,
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


def test_confirm_booking_success(db_session):
    booking = create_booking(db_session)

    with (
        patch("app.celery_app.tasks.time.sleep"),
        patch("app.celery_app.tasks.random.random", return_value=0.5),
    ):
        result = confirm_booking.run(booking.id)

    db_session.refresh(booking)
    assert result == {"status": "confirmed"}
    assert booking.status == StatusEnum.CONFIRMED


def test_confirm_booking_retry_on_external_failure(db_session):
    booking = create_booking(db_session)

    with (
        patch("app.celery_app.tasks.time.sleep"),
        patch("app.celery_app.tasks.random.random", return_value=0.1),
        patch.object(confirm_booking, "retry", side_effect=Retry()) as retry_mock,
    ):
        with pytest.raises(Retry):
            confirm_booking.run(booking.id)

    db_session.refresh(booking)
    assert booking.status == StatusEnum.PENDING
    retry_mock.assert_called_once()


def test_confirm_booking_sets_failed_status_after_retries(db_session):
    booking = create_booking(db_session)

    with (
        patch("app.celery_app.tasks.time.sleep"),
        patch("app.celery_app.tasks.random.random", return_value=0.1),
        patch.object(confirm_booking.request, "retries", confirm_booking.max_retries),
    ):
        result = confirm_booking.run(booking.id)

    db_session.refresh(booking)
    assert result == {"status": "failed"}
    assert booking.status == StatusEnum.FAILED


def test_confirm_booking_is_idempotent_for_final_status(db_session):
    booking = create_booking(db_session, status=StatusEnum.CONFIRMED)

    with (
        patch("app.celery_app.tasks.time.sleep") as sleep_mock,
        patch("app.celery_app.tasks.random.random") as random_mock,
    ):
        result = confirm_booking.run(booking.id)

    assert result == {"status": "confirmed"}
    sleep_mock.assert_not_called()
    random_mock.assert_not_called()


def test_confirm_booking_returns_error_for_missing_booking(db_session):
    result = confirm_booking.run(999999)

    assert result == {"error": "Бронь не найдена"}
