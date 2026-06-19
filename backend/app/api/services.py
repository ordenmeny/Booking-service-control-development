from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models import Booking
from app.api.schemas import CreateBooking
from app.core.custom_types import BookID


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
