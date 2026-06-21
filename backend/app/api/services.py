from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.models import Booking
from app.api.schemas import CreateBooking
from app.core.custom_types import BookID, StatusType


class BookingService:
    @staticmethod
    def create_booking(schema: CreateBooking, session: Session) -> Booking:
        model = Booking(
            name=schema.name,
            datetime=schema.datetime,
            service_type=schema.service_type,
        )

        session.add(model)
        session.commit()
        session.refresh(model)

        return model

    @staticmethod
    def get_booking_by_id(
        session: Session,
        booking_id: BookID,
    ) -> Booking | None:
        stmt = select(Booking).where(Booking.id == booking_id)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_booking_list(
        session: Session,
        status: StatusType,
        skip: int = 0,
        limit: int = 10,
    ):
        count_stmt = (
            select(func.count()).select_from(Booking).filter(Booking.status == status)
        )
        total = session.execute(count_stmt).scalar_one()

        stmt = (
            select(Booking).filter(Booking.status == status).offset(skip).limit(limit)
        )
        result = session.execute(stmt)
        bookings = list(result.scalars().all())

        return bookings, total

    @staticmethod
    def delete_booking_by_id(session: Session, booking: Booking) -> None:
        session.delete(booking)
        session.commit()
