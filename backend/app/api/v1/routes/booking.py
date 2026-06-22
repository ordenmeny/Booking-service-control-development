import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from starlette.responses import JSONResponse

from app.api.models import StatusEnum
from app.api.rate_limit import check_booking_rate_limit
from app.api.schemas import CreateBooking, ReadBooking, ReadBookingPaginate
from app.api.services import BookingService
from app.celery_app.tasks import confirm_booking
from app.core.custom_types import BookID, StatusType
from app.db.deps import SyncSessionDep

router = APIRouter(tags=["bookings"])


logger = logging.getLogger(__name__)


@router.post("/bookings", response_model=ReadBooking)
def create_booking(
    request: Request,
    session: SyncSessionDep,
    schema: CreateBooking,
) -> Any:
    check_booking_rate_limit(request)
    booking = BookingService.create_booking(schema, session)
    confirm_booking.delay(booking.id)
    return booking


@router.get("/bookings/{booking_id}", response_model=ReadBooking)
def get_booking_by_id(session: SyncSessionDep, booking_id: BookID) -> Any:
    booking = BookingService.get_booking_by_id(session, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Бронь не найдена",
        )

    return booking


@router.get("/bookings")
def list_bookings(
    session: SyncSessionDep,
    status: StatusType,
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(
        10, ge=1, le=100, description="Максимальное количество записей в ответе"
    ),
) -> ReadBookingPaginate:
    bookings, total = BookingService.get_booking_list(session, status, skip, limit)
    return ReadBookingPaginate(
        items=bookings,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.delete("/bookings/{booking_id}")
def delete_bookings(
    session: SyncSessionDep,
    booking_id: BookID,
) -> Any:
    booking_to_delete = BookingService.get_booking_by_id(session, booking_id)

    if booking_to_delete is None:
        raise HTTPException(
            status_code=404,
            detail="Бронь не найдена",
        )

    if booking_to_delete.status == StatusEnum.PENDING:
        BookingService.delete_booking_by_id(session, booking_to_delete)
        return JSONResponse(content="deleted", status_code=200)

    return JSONResponse(
        content="You can`t cancel confirmed or failed booking", status_code=403
    )
