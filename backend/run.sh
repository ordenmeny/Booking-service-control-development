#!/bin/sh
set -e

cd /app/backend || exit 1

# Celery worker
uv run celery -A app.celery_app.main.celery worker --loglevel=info &

# Flower
uv run celery -A app.celery_app.main.celery flower --port=5555 &

# FastAPI-app
exec uv run gunicorn main:app -c gunicorn_conf.py