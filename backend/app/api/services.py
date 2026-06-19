from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import Booking
from app.api.schemas import CreateBooking


class BookingService:
    @staticmethod
    async def create_booking(schema: CreateBooking, session: AsyncSession):
        model = Booking(
            name=schema.name,
            datetime=schema.datetime,
            service_type=schema.service_type,
        )

        session.add(model)
        await session.commit()
        await session.refresh(model)

        return model
