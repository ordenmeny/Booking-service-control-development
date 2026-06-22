import logging
import random
import time

from app.api.models import StatusEnum
from app.api.services import BookingService
from app.celery_app.main import celery
from app.core.custom_types import BookID
from app.db.helper import sync_sessionmanager

logger = logging.getLogger(__name__)


class ExternalServiceError(Exception):
    pass


@celery.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_jitter=True,
    soft_time_limit=10,
    time_limit=12,
)
def confirm_booking(self, booking_id: BookID):
    session = sync_sessionmanager.get_session()
    booking = None

    try:
        booking = BookingService.get_booking_by_id(session, booking_id)
        if booking is None:
            return {"error": "Бронь не найдена"}

        # идемпотентность: если статус уже финальный, сразу возвращаем
        if booking.status in (StatusEnum.CONFIRMED, StatusEnum.FAILED):
            logger.info(
                "Booking already has final status",
                extra={"booking_id": booking_id, "status": booking.status.value},
            )
            return {"status": booking.status.value}

        # Имитация бизнес-логики (задержка)
        time.sleep(5)

        # Сбой с вероятностью 15%
        if random.random() < 0.15:
            raise ExternalServiceError("Сбой внешнего сервиса (имитация)")

        # Успех
        booking.status = StatusEnum.CONFIRMED
        session.commit()
        session.refresh(booking)

        logger.info(
            "Mock notification sent",
            extra={"booking_id": booking_id, "status": StatusEnum.CONFIRMED.value},
        )
        return {"status": "confirmed"}

    except ExternalServiceError as e:
        logger.error(
            "External service failed while confirming booking",
            extra={"booking_id": booking_id, "error": str(e)},
        )

        if booking is not None:
            if self.request.retries < self.max_retries:
                session.rollback()
                countdown = min(2**self.request.retries, 60)
                logger.warning(
                    "Retry booking confirmation",
                    extra={
                        "booking_id": booking_id,
                        "countdown": countdown,
                        "retry": self.request.retries + 1,
                        "max_retries": self.max_retries,
                    },
                )
                raise self.retry(exc=e, countdown=countdown)

            try:
                if booking.status not in (StatusEnum.CONFIRMED, StatusEnum.FAILED):
                    booking.status = StatusEnum.FAILED
                    session.commit()
                    session.refresh(booking)
                    logger.info(
                        "Booking status changed to failed",
                        extra={
                            "booking_id": booking_id,
                            "status": StatusEnum.FAILED.value,
                        },
                    )
                else:
                    logger.info(
                        "Booking already has final status",
                        extra={
                            "booking_id": booking_id,
                            "status": booking.status.value,
                        },
                    )
                return {
                    "status": "failed"
                    if booking.status == StatusEnum.FAILED
                    else booking.status.value
                }
            except Exception as commit_error:
                logger.error(
                    "Could not update booking status to failed",
                    extra={"booking_id": booking_id, "error": str(commit_error)},
                )
                session.rollback()
                return {"error": "Не удалось обновить статус"}
        else:
            return {"error": "Бронь не найдена при обработке исключения"}

    except Exception as e:
        logger.exception(
            "Unexpected booking confirmation error",
            extra={"booking_id": booking_id, "error": str(e)},
        )
        session.rollback()
        return {"error": "Неожиданная ошибка обработки"}

    finally:
        session.close()
