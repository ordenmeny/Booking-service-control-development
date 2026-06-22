from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase

from app.core.custom_types import BookID


class Base(DeclarativeBase):
    type_annotation_map = {
        BookID: Integer,
    }
