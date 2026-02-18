# Oneshell means one can run multiple lines in a recipe in the same shell, so one doesn't have to
# chain commands together with semicolon
.ONESHELL:
SHELL=/bin/bash
PACKAGE=src

.PHONY: help python-version
.DEFAULT_GOAL=help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

# If .env file exists, include it and export its variables
ifeq ($(shell test -f .env && echo 1),1)
    include .env
    export
endif

install: ## Installs the development version of the package
	uv sync --frozen

python-version: ## Checks the python version used in the environment
	uv lock --locked
	uv run python --version

lint: ## Lint code with ruff
	uv lock --locked
	uv run --module ruff format ${PACKAGE} --check --diff
	uv run --module ruff check ${PACKAGE}

format: ## Run ruff for all package files. CHANGES CODE
	uv lock --locked
	uv run --module ruff format ${PACKAGE}
	uv run --module ruff check ${PACKAGE} --fix --show-fixes

format-unsafe: ## Run ruff for all package files. CHANGES CODE
	uv lock --locked
	uv run --module ruff format ${PACKAGE}
	uv run --module ruff check ${PACKAGE} --fix --unsafe-fixes --show-fixes

run-worker: ## Run Hatchet general worker
	uv lock --locked
	uv run --module worker.main

test-task-logic: ## Run Hatchet task-logic tests
	uv lock --locked
	uv run --with pytest python -m pytest tests/test_hatchet_task_logic.py
