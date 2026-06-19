import uvicorn
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.admin import admin

app = FastAPI()

app.include_router(api_router)

admin(app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
