from app.api.models import StatusEnum
from app.api.services import BookingService
from app.celery_app.main import celery
from app.core.custom_types import BookID
from app.db.helper import sync_sessionmanager


@celery.task(
    bind=True,
    max_retries=3,
    soft_time_limit=10,
    time_limit=12,
)
def confirm_booking(self, booking_id: BookID):
    session = sync_sessionmanager.get_session()

    try:
        booking = BookingService.get_booking_by_id(session, booking_id)
        if booking is None:
            return {"error": "Бронь не найдена"}

        booking.status = StatusEnum.CONFIRMED
        session.commit()
        session.refresh(booking)
        return {"status": "confirmed"}

    except Exception as exc:
        session.rollback()
        # Повторная попытка с задержкой (60 секунд)
        self.retry(exc=exc, countdown=60)
    finally:
        session.close()
