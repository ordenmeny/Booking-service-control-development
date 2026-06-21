from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.admin import admin

app = FastAPI()

app.include_router(api_router)

admin(app)
