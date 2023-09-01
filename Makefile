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
ci: tests pylint mypy  ## Run all checks (tests, pylint, mypy etc.)

.PHONY: tests
tests:  ## Run tests from virtual environment
	@echo "Running tests ..."
	$(PYTHON) -m unittest discover -s './tests' -p 'test_*.py' -v

.PHONY: yapf
yapf:  ## Format python code with yapf
	@echo "Running Yapf ..."
	$(PYTHON) -m yapf --recursive --in-place $(SRC_DIR) $(TEST_DIR)

.PHONY: pylint
pylint:  ## Run pylint
	@echo "Running Pylint report ..."
	$(PYTHON) -m pylint --rcfile=.pylintrc $(SRC_DIR)

.PHONY: mypy
mypy:  ## Run mypy
	@echo "Running Mypy report ..."
	$(PYTHON) -m mypy --ignore-missing-imports $(SRC_DIR)

.PHONY: release
release:  ## Release to Pypi
	$(PYTHON) setup.py sdist
	$(PYTHON) -m twine upload dist/*
