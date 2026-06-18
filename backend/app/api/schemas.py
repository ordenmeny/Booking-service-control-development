from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.core.custom_types import BookID


class CreateBooking(BaseModel):
    name: str
    datetime: datetime
    service_type: str


class ReadBooking(BaseModel):
    id: BookID
    name: str
    datetime: datetime
    service_type: str
    status: Literal["pending", "confirmed", "failed"]
