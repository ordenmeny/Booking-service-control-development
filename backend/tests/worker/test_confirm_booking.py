from datetime import datetime
from unittest.mock import patch

from app.api.models import Booking, StatusEnum
from app.celery_app.tasks import confirm_booking
from app.db.helper import sync_sessionmanager


def test_confirm_booking_success():
    session = sync_sessionmanager.get_session()

    booking = Booking(
        name="Worker",
        datetime=datetime.utcnow(),
        service_type="test",
    )

    session.add(booking)
    session.commit()
    session.refresh(booking)
    booking_id = booking.id

    session.close()

    with (
        patch("app.celery_app.tasks.time.sleep"),
        patch("app.celery_app.tasks.random.random", return_value=0.5),
    ):
        result = confirm_booking.run(booking_id)

    session = sync_sessionmanager.get_session()

    booking = session.get(Booking, booking_id)

    assert result == {"status": "confirmed"}
    assert booking.status == StatusEnum.CONFIRMED

    session.delete(booking)
    session.commit()
    session.close()
