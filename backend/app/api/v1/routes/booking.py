from typing import Any

from fastapi import APIRouter

from app.api.schemas import CreateBooking, ReadBooking
from app.api.services import BookingService
from app.db.deps import SessionDep

router = APIRouter(prefix="/api/v1/booking", tags=["booking"])


@router.post("/bookings", response_model=ReadBooking)
async def create_booking(
    session: SessionDep,
    schema: CreateBooking,
) -> Any:
    return await BookingService.create_booking(schema, session)


@router.get("/bookings/{id}")
async def get_booking_by_id() -> None:
    pass


@router.get("/bookings")
async def list_bookings() -> None:
    pass


@router.delete("/bookings/{id}")
async def delete_bookings() -> None:
    pass
