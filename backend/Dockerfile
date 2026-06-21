FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock /app/
COPY backend/pyproject.toml backend/README.md /app/backend/
COPY backend/run.sh /run.sh
RUN chmod +x /run.sh

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package backend --locked --no-dev --no-install-project

COPY backend/run.sh /run.sh
RUN chmod +x /run.sh

COPY backend/test.sh /test.sh
RUN chmod +x /test.sh

COPY backend/alembic.ini backend/main.py backend/gunicorn_conf.py /app/backend/
COPY backend/alembic /app/backend/alembic

COPY backend/app /app/backend/app
COPY backend/tests /app/backend/tests

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package backend --locked --no-dev

EXPOSE 8000

CMD ["/run.sh"]