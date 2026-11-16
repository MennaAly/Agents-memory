# Memory Service

Multi-tenant REST API that stores and searches long-term memories for AI agents.

## Install

Requires [uv](https://docs.astral.sh/uv/) (`brew install uv`). uv fetches Python 3.12 automatically.

```sh
uv sync                 # create .venv and install all deps (incl. dev)
cp .env.example .env    # then set SECRET_KEY
docker compose up -d db # start PostgreSQL (or point DATABASE_URL at your own server)
```

The database is PostgreSQL. `DATABASE_URL` is required; tests also need the server running.

## Run migrations

```sh
uv run python manage.py migrate
```

## Run the server

```sh
uv run python manage.py runserver
```

- Health check: http://127.0.0.1:8000/api/health
- API docs (Swagger UI): http://127.0.0.1:8000/api/docs  
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

## Run tests

```sh
uv run pytest
```

## Lint & format

```sh
uv run ruff check .
uv run ruff format .
```
