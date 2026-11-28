# Jobseek

Job vacancy aggregator API built with FastAPI and PostgreSQL.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.13 (managed by uv via `.python-version`)
- [Docker](https://docs.docker.com/get-docker/) (for local PostgreSQL)

## Setup

```bash
make setup
```

Or step by step: `make sync`, copy `.env.example` → `.env`, then `make up`, `make migrate`.

## Run

```bash
make up      # PostgreSQL (once)
make migrate # after schema changes
make dev     # API with hot reload
```

Health check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

Useful targets: `make help`, `make down`, `make check`, `make revision msg="…"`.

## Jobs

Providers (no API keys): **Arbeitnow** (EU/ATS) and **Jobicy** (remote worldwide).

Sync into PostgreSQL:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jobs/sync
```

List stored jobs (paginated, default `page=1&limit=20`):

```bash
curl 'http://127.0.0.1:8000/api/v1/jobs?page=1&limit=20'
```

Filter (any combo of `q`, `location`, `remote`, `tag`):

```bash
curl 'http://127.0.0.1:8000/api/v1/jobs?q=python&location=berlin&remote=true&tag=devops&page=1&limit=20'
```

Get one job by id (URL-encode the id if it contains `:`):

```bash
curl 'http://127.0.0.1:8000/api/v1/jobs/jobicy%3A164483'
```

## Lint & types

```bash
make check
make format
```
