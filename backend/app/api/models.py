import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import BookID
from app.db.base import Base


class StatusEnum(enum.StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class Booking(Base):
    __tablename__ = "booking"

    id: Mapped[BookID] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    service_type: Mapped[str] = mapped_column(String(255))

    status: Mapped[StatusEnum] = mapped_column(
        Enum(
            StatusEnum,
            name="status_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=StatusEnum.PENDING,
        nullable=False,
        server_default="pending",
    )
