from celery import Celery

from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

celery = Celery(
    "app.celery_app.main",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend_url,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    include=[
        "app.celery_app.tasks",
    ],
    broker_transport_options={
        "visibility_timeout": 3600,
    },
    result_expires=7200,
    task_track_started=True,
)
