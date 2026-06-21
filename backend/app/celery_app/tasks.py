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

        # идемпотентность: если статус уже финальный, сразу возвращаем
        if booking.status in (StatusEnum.CONFIRMED, StatusEnum.FAILED):
            logger.info(f"Бронь {booking_id} уже в финальном статусе: {booking.status}")
            return {"status": booking.status.value}

        # Имитация бизнес-логики (задержка)
        time.sleep(5)

        # Сбой с вероятностью 15%
        if random.random() < 0.15:
            raise Exception("Сбой внешнего сервиса (имитация)")

        # Успех
        booking.status = StatusEnum.CONFIRMED
        session.commit()
        session.refresh(booking)

        logger.info(f"Mock-уведомление: бронь {booking_id} подтверждена")
        return {"status": "confirmed"}

    except Exception as e:
        logger.error(f"Ошибка при подтверждении брони {booking_id}: {e}")

        if booking is not None:
            try:
                # Если бронь уже была изменена, но статус ещё не финальный – ставим FAILED
                if booking.status not in (StatusEnum.CONFIRMED, StatusEnum.FAILED):
                    booking.status = StatusEnum.FAILED
                    session.commit()
                    session.refresh(booking)
                    logger.info(f"Статус брони {booking_id} изменён на FAILED")
                else:
                    logger.info("Бронь уже в финальном статусе, ничего не меняем")
                return {
                    "status": "failed"
                    if booking.status == StatusEnum.FAILED
                    else booking.status.value
                }
            except Exception as commit_error:
                logger.error(f"Не удалось обновить статус FAILED: {commit_error}")
                session.rollback()
                return {"error": "Не удалось обновить статус"}
        else:
            return {"error": "Бронь не найдена при обработке исключения"}

    finally:
        session.close()
