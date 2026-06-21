#!/bin/sh
set -e

cd /app/backend || exit 1
uv add pytest httpx pytest-anyio
uv run pytest tests -v
uv remove pytest httpx pytest-anyio