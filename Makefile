.PHONY: help fmt checks pylint mypy env test-env

SHELL=/bin/bash
SRC_DIR=pyavatar

help: ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

checks: pylint mypy  ## Run all checks (pylint, mypy)

fmt: test-env ## Format python code with black
	@echo "Running Black ..."
	@source env/bin/activate \
		&& black --line-length 79 --target-version py38 $(SRC_DIR)

pylint: test-env ## Run pylint
	@echo "Running Pylint report ..."
	@source env/bin/activate || true \
		&& pylint --rcfile=.pylintrc $(SRC_DIR)

mypy: env test-env ## Run mypy
	@echo "Running Mypy report ..."
	@source env/bin/activate || true \
		&& mypy --ignore-missing-imports $(SRC_DIR)

env:
	@./bin/build-env

test-env:
	@./bin/dev-deps
