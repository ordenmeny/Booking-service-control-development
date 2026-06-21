import logging
import random
import time

from app.api.models import StatusEnum
from app.api.services import BookingService
from app.celery_app.main import celery
from app.core.custom_types import BookID
from app.db.helper import sync_sessionmanager

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    max_retries=0,
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

        # Имитация бизнес-логики (задержка)
        time.sleep(3)

        # имитация сбоя внешнего сервиса с вероятностью 15%
        if random.random() < 0.15:
            raise Exception("Сбой внешнего сервиса (имитация)")

        booking.status = StatusEnum.CONFIRMED

        session.commit()
        session.refresh(booking)

        # Логируем mock-отправку уведомления
        logger.info(f"Mock-уведомление: бронь {booking_id} подтверждена")

        return {"status": "confirmed"}

    except Exception as e:
        logger.error(f"Ошибка при подтверждении брони {booking_id}: {e}")

        if booking is not None:
            try:
                booking.status = StatusEnum.FAILED
                session.commit()
                session.refresh(booking)
                logger.info(f"Статус брони {booking_id} изменён на FAILED")
                return {"status": "failed"}
            except Exception as commit_error:
                logger.error(f"Не удалось обновить статус FAILED: {commit_error}")
                session.rollback()
                return {"error": "Не удалось обновить статус"}
        else:
            return {"error": "Бронь не найдена при обработке исключения"}

    finally:
        session.close()
