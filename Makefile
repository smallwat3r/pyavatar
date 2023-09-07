SHELL    = /bin/bash
SRC_DIR  = pyavatar
TEST_DIR = tests

.PHONY: help
help:  ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

.PHONY: clean
clean:  ## Clean repo
	find . -type d -name  "__pycache__" -exec rm -r {} +

VENV          = venv
VENV_PYTHON   = $(VENV)/bin/python
SYSTEM_PYTHON = $(or $(shell which python3.10), $(shell which python))
PYTHON        = $(or $(wildcard $(VENV_PYTHON)), $(SYSTEM_PYTHON))

$(VENV_PYTHON):
	rm -rf $(VENV)
	$(SYSTEM_PYTHON) -m venv $(VENV)

.PHONY: venv
venv: $(VENV_PYTHON)  ## Create a Python virtual environment

.PHONY: deps
deps:  ## Install Python requirements in virtual environment
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt -r dev-requirements.txt

.PHONY: ci
ci: tests ruff mypy  ## Run all checks (tests, pylint, mypy etc.)

.PHONY: tests
tests:  ## Run tests from virtual environment
	@echo "Running tests..."
	$(PYTHON) -m pytest $(TEST_DIR)

.PHONY: yapf
yapf:  ## Format python code with yapf
	@echo "Running Yapf..."
	$(PYTHON) -m yapf --recursive --in-place $(SRC_DIR) $(TEST_DIR)

.PHONY: ruff
ruff:  ## Run ruff
	@echo "Running Ruff report..."
	$(PYTHON) -m ruff $(SRC_DIR) $(TEST_DIR)

.PHONY: mypy
mypy:  ## Run mypy
	@echo "Running Mypy report..."
	$(PYTHON) -m mypy --ignore-missing-imports $(SRC_DIR)

.PHONY: release
release:  ## Release to Pypi
	rm -rf dist pyavatar.egg_info || true
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine upload dist/*
