# Jobseek

Job vacancy aggregator API built with FastAPI.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.13 (managed by uv via `.python-version`)

## Setup

```bash
uv sync --all-groups
uv run pre-commit install
cp .env.example .env
```

## Run

```bash
uv run fastapi dev app/main.py
```

Health check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

## Jobs

Sync from Arbeitnow into local `data/jobs.json`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jobs/sync
```

List stored jobs (default `limit=100`):

```bash
curl 'http://127.0.0.1:8000/api/v1/jobs?limit=20'
```

Filter (any combo of `q`, `location`, `remote`, `tag`):

```bash
curl 'http://127.0.0.1:8000/api/v1/jobs?q=python&location=berlin&remote=true&tag=devops&limit=20'
```

## Lint & types

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```
