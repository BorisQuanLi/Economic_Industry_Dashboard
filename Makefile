# --- 1. Variables & Dynamic Discovery ---
# These define the project metadata and find your services automatically.
PYTHON_VERSION := 3.12.3
VENV           := .venv
BIN            := $(VENV)/bin
PYTHON         := $(BIN)/python
PIP            := $(BIN)/pip

# Dynamically find directories with requirements.txt or pom.xml
PY_SERVICES   := $(shell find . -maxdepth 2 -name "requirements.txt" -exec dirname {} \;)
JAVA_SERVICES := $(shell find . -maxdepth 2 -name "pom.xml" -exec dirname {} \;)
SERVICES      := $(PY_SERVICES) $(JAVA_SERVICES)

# Git Worktree Discovery
WORKTREES     := $(shell git worktree list --porcelain | grep "^worktree" | awk '{print $$2}')
AI_AGENT_DIR  := $(shell git worktree list | grep "task-consolidate" | awk '{print $$1}')

# --- 2. Phony Targets ---
# Prevents conflicts with files of the same name and improves 'make help'
.PHONY: help setup init lint test build up down clean list-worktrees check-java check-python

# --- 3. Implementation ---

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check-python: ## Verify local environment meets project standards
	@actual=$$( python3 -V | cut -d' ' -f2 ); \
	if [ "$$actual" != "$(PYTHON_VERSION)" ]; then \
		echo "⚠️  Warning: Project optimized for $(PYTHON_VERSION), found $$actual"; \
	fi

check-java: ## Verify Java presence for local (non-Docker) Spark runs
	@command -v java >/dev/null 2>&1 || (echo "⚠️  Note: Java not found. Local PySpark (non-Docker) will fail, but Docker runs are unaffected."; exit 0)

setup: check-python ## Initialize the environment (VENV + Dependencies)
	@echo "🚀 Starting holistic project setup..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "✅ Created .env"; fi
	@test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install ruff pytest pytest-cov
	@for dir in $(PY_SERVICES); do \
		if [ -f $$dir/requirements.txt ]; then $(PIP) install -r $$dir/requirements.txt; fi \
	done

init: setup ## One-command startup (Host Setup + Docker)
	docker compose up --build -d
	@echo "✨ System live at http://localhost:8501"

lint: ## Run linting across all services or a specific SERVICE (e.g., make lint SERVICE=etl_service)
	@if [ "$(SERVICE)" ]; then \
		$(BIN)/ruff check $(SERVICE); \
	else \
		$(BIN)/ruff check $(SERVICES); \
	fi

test: ## Run tests for all services or a specific SERVICE
	@if [ "$(SERVICE)" ]; then \
		$(BIN)/pytest $(SERVICE); \
	else \
		for service in $(SERVICES); do $(BIN)/pytest $$service; done \
	fi

build: ## Build docker-compose services
	docker compose build

up: ## Start all services in the background
	docker compose up -d

down: ## Stop and remove containers
	docker compose down

clean: ## Remove temporary files, caches, and the virtual environment
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

list-worktrees: ## List all active dev-environments (worktrees)
	@echo "🌳 Active Worktrees:"
	@echo "$(WORKTREES)" | tr ' ' '\n'
