# Booking Service

Backend-сервис для записи на встречи. API создаёт бронь в статусе `pending`, Celery-воркер асинхронно подтверждает её или переводит в `failed`, Redis используется как broker/result backend, PostgreSQL - как основное хранилище.

## Стек

* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* Celery
* Redis
* Docker Compose
* Pytest

## Режимы Запуска

В проекте разделены два сценария:

* **prod-like** - весь стек запускается через Docker Compose: API, Celery worker, Flower, PostgreSQL, Redis;
* **dev** - в Docker запускается только инфраструктура, а API, worker, Flower, миграции и тесты запускаются локально через `uv`/`make`.

Такой подход сохраняет воспроизводимый полный запуск и при этом оставляет удобный локальный цикл разработки.

## Prod-like Запуск

Создать env-файл:

```bash
cp .env.example .env
```

Запустить полный стек:

```bash
make prod-up
```

Или напрямую:

```bash
docker compose --env-file .env -f docker-compose.yml up --build
```

Будут подняты:

* API: `http://localhost:8000`
* Flower: `http://localhost:5555`
* PostgreSQL внутри Docker-сети
* Redis внутри Docker-сети

Миграции в этом режиме применяются автоматически перед стартом API.

## Dev Запуск

Создать dev env-файл:

```bash
cp .env.dev.example .env.dev
```

Поднять dev-инфраструктуру:

```bash
make dev-infra
```

Применить миграции:

```bash
make migrate
```

Запустить API локально:

```bash
make dev-api
```

В отдельном терминале запустить Celery worker:

```bash
make dev-worker
```

Flower при необходимости:

```bash
make dev-flower
```

В dev-режиме доступны:

* API: `http://localhost:8000`
* PostgreSQL: `localhost:5432`
* Redis: `localhost:6379`
* pgAdmin: `http://localhost:8080`
* RedisInsight: `http://localhost:5540`

## Тесты

Тесты запускаются против dev-инфраструктуры:

```bash
make dev-infra
make migrate
make test
```

## Миграции

Применить миграции:

```bash
make migrate
```

Создать новую миграцию:

```bash
make migration name="describe change"
```

## Технические Решения

**FastAPI** выбран как компактный фреймворк для REST API с удобной интеграцией Pydantic-схем.

**SQLAlchemy + Alembic** используются для работы с PostgreSQL через ORM и версионирования схемы БД без ручных SQL-запросов.

**Celery + Redis** отделяют обработку брони от HTTP-запроса. API создаёт запись и ставит задачу в очередь, worker меняет статус асинхронно.

**Идемпотентность задачи** обеспечивается проверкой текущего статуса брони перед обработкой. Если бронь уже в финальном статусе `confirmed` или `failed`, повторный запуск задачи не выполняет бизнес-логику заново.

**Разделение dev/prod-like** сделано на уровне compose-файлов, env-файлов и команд запуска. Код приложения остаётся общим для всех режимов.
