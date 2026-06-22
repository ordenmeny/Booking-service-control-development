import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings

# 1. Включить JSON-логи: вызвать setup_logging() при старте процесса
#    (API, Celery worker, отдельная команда).
# 2. Писать структурные поля через extra:
#    logger.info("Booking confirmed", extra={"booking_id": 1, "status": "confirmed"})
# 3. Имена полей в extra можно выбирать свободно, но нельзя пересекаться
#    со стандартными атрибутами LogRecord: message, levelname, name, created и т.д.

STANDARD_LOG_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in STANDARD_LOG_RECORD_ATTRS and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)
