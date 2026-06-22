#!/bin/sh
set -e

cd /app/backend || exit 1

exec uv run --no-sync celery -A app.celery_app.main.celery flower --port=5555
