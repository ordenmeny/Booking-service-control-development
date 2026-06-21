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

COPY backend /app/backend/
COPY backend/alembic /app/backend/alembic

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package backend --locked --no-dev

EXPOSE 8000

CMD ["/run.sh"]