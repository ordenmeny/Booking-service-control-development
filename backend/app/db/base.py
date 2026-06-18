from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from app.core.custom_types import BookID


class Base(DeclarativeBase):
    id: Mapped[BookID] = mapped_column(primary_key=True)
