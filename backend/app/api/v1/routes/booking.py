import logging
from typing import Any

from fastapi import APIRouter

from app.api.schemas import CreateBooking, ReadBooking, BookingStatus
from app.api.services import BookingService
from app.celery_app.tasks import confirm_booking
from app.core.custom_types import BookID
from app.db.deps import SyncSessionDep

router = APIRouter(prefix="/api/v1/booking", tags=["booking"])


logger = logging.getLogger(__name__)


@router.post("/bookings", response_model=ReadBooking)
def create_booking(
    session: SyncSessionDep,
    schema: CreateBooking,
) -> Any:
    booking = BookingService.create_booking(schema, session)
    confirm_booking.delay(booking.id)
    return booking


@router.get("/bookings/{booking_id}", response_model=BookingStatus)
def get_booking_by_id(session: SyncSessionDep, booking_id: BookID) -> Any:
    booking = BookingService.get_booking_by_id(session, booking_id)
    if booking is None:
        return {"error": "Бронь не найдена"}
    return booking


@router.get("/bookings")
def list_bookings() -> None:
    pass


@router.delete("/bookings/{id}")
def delete_bookings() -> None:
    pass
