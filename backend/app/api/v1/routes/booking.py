from typing import Any

from fastapi import APIRouter

from app.api.schemas import CreateBooking, ReadBooking
from app.api.services import BookingService
from app.celery_app.tasks import confirm_booking
from app.db.deps import SyncSessionDep

router = APIRouter(prefix="/api/v1/booking", tags=["booking"])


@router.post("/bookings", response_model=ReadBooking)
def create_booking(
    session: SyncSessionDep,
    schema: CreateBooking,
) -> Any:
    booking = BookingService.create_booking(schema, session)
    confirm_booking.delay(booking.id)
    return booking


@router.get("/bookings/{id}")
async def get_booking_by_id() -> None:
    pass


@router.get("/bookings")
async def list_bookings() -> None:
    pass


@router.delete("/bookings/{id}")
async def delete_bookings() -> None:
    pass
