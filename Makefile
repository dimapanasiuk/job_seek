.PHONY: help sync setup up down wait-db migrate revision import-json dev lint format typecheck check

COMPOSE ?= docker compose
UV ?= uv run

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

sync: ## Install Python dependencies
	uv sync --all-groups

setup: sync ## First-time setup: deps, .env, pre-commit, db, migrations
	@test -f .env || cp .env.example .env
	$(UV) pre-commit install
	$(MAKE) up
	$(MAKE) wait-db
	$(MAKE) migrate

up: ## Start PostgreSQL
	$(COMPOSE) up -d

down: ## Stop PostgreSQL
	$(COMPOSE) down

wait-db: ## Wait until PostgreSQL is ready
	@echo "Waiting for PostgreSQL..."
	@until $(COMPOSE) exec -T postgres pg_isready -U jobseek -d jobseek >/dev/null 2>&1; do \
		sleep 1; \
	done
	@echo "PostgreSQL is ready."

migrate: ## Apply database migrations
	$(UV) alembic upgrade head

revision: ## Create a new Alembic revision (msg="description")
	@test -n "$(msg)" || (echo 'Usage: make revision msg="description"' && exit 1)
	$(UV) alembic revision --autogenerate -m "$(msg)"

import-json: ## Import data/jobs.json into PostgreSQL
	$(UV) python scripts/import_jobs_json.py

dev: ## Run API with hot reload
	$(UV) fastapi dev app/main.py

lint: ## Run Ruff linter
	$(UV) ruff check .

format: ## Format code with Ruff
	$(UV) ruff format .

typecheck: ## Run Pyright
	$(UV) pyright

check: lint typecheck ## Lint + typecheck
