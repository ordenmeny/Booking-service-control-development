ENV_FILE ?= .env.dev
COMPOSE_ENV_CLEAN = env -u APP_ENV -u ECHO -u DB_HOST -u DB_PORT -u DB_USER -u DB_PASS -u DB_NAME -u PGADMIN_DEFAULT_EMAIL -u PGADMIN_DEFAULT_PASSWORD -u PGADMIN_PORT -u REDIS_HOST -u REDIS_PORT -u REDIS_PASSWORD -u REDIS_BROKER_DB -u REDIS_RESULT_DB -u REDISINSIGHT_PORT
COMPOSE_DEV = $(COMPOSE_ENV_CLEAN) docker compose --env-file $(ENV_FILE) -f docker-compose.dev.yml
COMPOSE_PROD = docker compose --env-file .env -f docker-compose.yml
BACKEND_DIR = backend

.PHONY: dev-infra dev-infra-down dev-api dev-worker dev-flower migrate migration test prod-up prod-down

# set -a && . ../$(ENV_FILE) && set +a загружает значения из .env.dev
# как переменные окружения, чтобы config.py видел dev-настройки вместо .env.

dev-infra:
	$(COMPOSE_DEV) up -d

dev-infra-down:
	$(COMPOSE_DEV) down

dev-api:
	cd $(BACKEND_DIR) && set -a && . ../$(ENV_FILE) && set +a && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-worker:
	cd $(BACKEND_DIR) && set -a && . ../$(ENV_FILE) && set +a && uv run celery -A app.celery_app.main.celery worker --loglevel=info

dev-flower:
	cd $(BACKEND_DIR) && set -a && . ../$(ENV_FILE) && set +a && uv run celery -A app.celery_app.main.celery flower --port=5555

migrate:
	cd $(BACKEND_DIR) && set -a && . ../$(ENV_FILE) && set +a && uv run alembic upgrade head

migration:
	cd $(BACKEND_DIR) && set -a && . ../$(ENV_FILE) && set +a && uv run alembic revision --autogenerate -m "$(name)"

test:
	cd $(BACKEND_DIR) && set -a && . ../$(ENV_FILE) && set +a && uv run pytest tests -v

prod-up:
	$(COMPOSE_PROD) up --build

prod-down:
	$(COMPOSE_PROD) down
