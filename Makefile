.PHONY: help fmt checks pylint mypy test env test-env

SHELL=/bin/bash
SRC_DIR=pyavatar

help: ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

checks: tests pylint mypy  ## Run all checks (tests, pylint, mypy)

fmt: test-env ## Format python code with yapf
	@echo "Running Yapf ..."
	@source env/bin/activate \
		&& yapf --recursive --in-place $(SRC_DIR)

pylint: test-env ## Run pylint
	@echo "Running Pylint report ..."
	@source env/bin/activate || true \
		&& pylint --rcfile=.pylintrc $(SRC_DIR)

mypy: env test-env ## Run mypy
	@echo "Running Mypy report ..."
	@source env/bin/activate || true \
		&& mypy --ignore-missing-imports $(SRC_DIR)

tests: env test-env ## Run unit tests
	@echo "Running tests ..."
	@./bin/run-tests

env:
	@./bin/build-env

test-env:
	@./bin/dev-deps
