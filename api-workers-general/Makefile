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

run-taskiq-scheduler: # Run taskiq scheduler. Only one scheduler can be run at a time. It only sends tasks to the workers, doesn't execute them
	uv lock --locked
	uv run --module taskiq scheduler worker.broker:scheduler -fsd -tp 'src/worker/tasks/*.py'

run-taskiq-workers: # Run 2 taskiq workers using threadpools ( Default )
	uv lock --locked
	RUN_MODE=worker uv run --module taskiq worker worker.broker:broker --workers 2 -fsd -tp 'src/worker/tasks/*.py'

run-taskiq-workers-processpool: # Run 2 taskiq workers using processpools
	uv lock --locked
	RUN_MODE=worker uv run --module taskiq worker worker.broker:broker --use-process-pool --workers 2 -fsd -tp ['src/worker/tasks/*.py']

run-taskiq-main: # Run taskiq main to test the workers and the broker
	uv lock --locked
	uv run --module main
