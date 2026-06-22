#!/bin/sh
set -e

cd /app/backend || exit 1

alembic upgrade head

exec uv run --no-sync gunicorn main:app -c gunicorn_conf.py
