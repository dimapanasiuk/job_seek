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
uv run fastapi dev src/jobseek/main.py
```

Health check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

## Lint & types

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```
