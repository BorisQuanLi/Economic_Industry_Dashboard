# --- 1. Variables & Dynamic Discovery ---
PYTHON_VERSION := 3.12.3
VENV           := .venv
BIN            := $(VENV)/bin
PYTHON         := $(BIN)/python
PIP            := uv pip

# Use your system runners when invoking through uv environment mappings
TEST_RUNNER    := pytest
LINT_RUNNER    := ruff check

# Dynamically discover services with requirements.txt or pom.xml
PY_SERVICES   := $(shell find . -maxdepth 2 -name "requirements.txt" -exec dirname {} \;)
JAVA_SERVICES := $(shell find . -maxdepth 2 -name "pom.xml" -exec dirname {} \;)
SERVICES      := $(PY_SERVICES) $(JAVA_SERVICES)

# Git Worktree Discovery
WORKTREES     := $(shell git worktree list --porcelain | grep "^worktree" | awk '{print $$2}')
AI_AGENT_DIR  := $(shell git worktree list | grep "task-consolidate" | awk '{print $$1}')

.PHONY: help setup init lint test build up down clean clean-gpu list-worktrees check-java check-python

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check-python: ## Verify local environment meets project standards
	@actual=$$( python3 -V | cut -d' ' -f2 ); \
	if [ "$$actual" != "$(PYTHON_VERSION)" ]; then \
		echo "⚠️  Warning: Project optimized for $(PYTHON_VERSION), found $$actual"; \
	fi

check-java: ## Verify Java presence for local PySpark runs
	@command -v java >/dev/null 2>&1 || (echo "⚠️  Note: Java not found. Local PySpark will fail, but Docker runs are unaffected."; exit 0)

setup: check-python ## Initialize the workspace using uv (creates .venv, installs all service dependencies)
	@echo "🚀 Initializing uv workspace..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "✅ Created .env"; fi
	@test -d $(VENV) || uv venv
	uv pip install ruff pytest pytest-cov
	@for dir in $(PY_SERVICES); do \
		if [ -f $$dir/requirements.txt ]; then \
			echo "📦 Installing dependencies for $$dir via uv..."; \
			uv pip install -r $$dir/requirements.txt; \
		fi \
	done
	@echo "✨ uv workspace ready."

init: setup ## One-command startup (Host uv Setup + Docker)
	docker compose up --build -d
	@echo "✨ System live at http://localhost:8501"

lint: ## Run linting across all services or a specific SERVICE (e.g., make lint SERVICE=etl_service)
	@if [ "$(SERVICE)" ]; then \
		$(LINT_RUNNER) $(SERVICE); \
	else \
		$(LINT_RUNNER) $(SERVICES); \
	fi

test: ## Run tests for all services or a specific SERVICE (e.g., make test SERVICE=etl_service)
	@if [ "$(SERVICE)" ]; then \
		if [ -f "$(SERVICE)/requirements.txt" ]; then uv pip install -q -r $(SERVICE)/requirements.txt; fi; \
		uv run pytest -o pythonpath=$(CURDIR)/$(SERVICE) $(SERVICE); \
	else \
		failed=""; \
		for service in $(SERVICES); do \
			clean_dir=$$(echo $$service | sed 's|^./||'); \
			if [ -d "$$service" ]; then \
				if [ -d "$$clean_dir/tests" ] || [ -d "$$clean_dir/test" ]; then \
					echo "🧪 Executing test matrix inside service: ./$$clean_dir"; \
					if [ -f "$$clean_dir/requirements.txt" ]; then \
						echo "📦 Resolving isolated runtime requirements for $$clean_dir..."; \
						uv pip install -q -r $$clean_dir/requirements.txt; \
					fi; \
					if [ "$$clean_dir" = "flask_backend" ]; then \
						uv run pytest -o "pythonpath=$(CURDIR)/$$clean_dir $(CURDIR)" $$clean_dir || failed="$$failed $$clean_dir"; \
					else \
						uv run pytest -o pythonpath=$(CURDIR)/$$clean_dir $$clean_dir || failed="$$failed $$clean_dir"; \
					fi; \
				fi; \
			fi; \
		done; \
		if [ -n "$$failed" ]; then \
			echo ""; \
			echo "❌ Test failures in:$$failed"; \
			exit 1; \
		fi; \
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
	@if [ -d "gpu_cache" ]; then \
		echo "🧹 Clearing GPU staging cache..."; \
		sudo rm -rf gpu_cache/*; \
	fi

clean-gpu: ## Targeted clearing of GPU staging volume
	sudo rm -rf gpu_cache/*

list-worktrees: ## List all active dev-environments (worktrees)
	@echo "🌳 Active Worktrees:"
	@echo "$(WORKTREES)" | tr ' ' '\n'
