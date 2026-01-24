# Oneshell means one can run multiple lines in a recipe in the same shell, so one doesn't have to
# chain commands together with semicolon
.ONESHELL:
SHELL=/bin/bash

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

run-ui: ## Run the fasthtml UI server
	uv lock --locked
	uv run --module uvicorn main:app --host 0.0.0.0 --port 5002