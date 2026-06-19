from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.models import Booking
from app.core.config import settings

engine = create_async_engine(
    settings.db_url,
    echo=True,
)


class UserAdmin(ModelView, model=Booking):
    column_list = [Booking.id, Booking.name, Booking.status, Booking.datetime]


def admin(app: FastAPI, engine=engine):
    Admin(app, engine).add_view(UserAdmin)
