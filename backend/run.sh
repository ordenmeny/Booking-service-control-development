#!/bin/sh
set -e

cd /app/backend || exit 1

# Migrations
alembic upgrade head

# Celery worker
uv run --no-sync celery -A app.celery_app.main.celery worker --loglevel=info &

# Flower
uv run --no-sync celery -A app.celery_app.main.celery flower --port=5555 &

# FastAPI-app
exec uv run --no-sync gunicorn main:app -c gunicorn_conf.py