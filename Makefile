.PHONY: help fmt pylint env test-env

SHELL=/bin/bash
SRC_DIR=pyavatar

help: ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

fmt: test-env ## Format python code with black
	@echo "Running Black ..."
	@source env/bin/activate \
		&& black --line-length 79 --target-version py38 $(SRC_DIR)

pylint: test-env ## Run pylint
	@echo "Running Pylint report ..."
	@source env/bin/activate || true \
		&& pylint --rcfile=.pylintrc $(SRC_DIR)

env:
	@./bin/build-env

test-env:
	@./bin/test-deps
