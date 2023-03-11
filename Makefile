.DEFAULT_GOAL := help
.PHONY: install format

### QUICK
# ¯¯¯¯¯¯¯

install: ## Install dependencies
	pip install -r requirements-dev.txt --upgrade --no-warn-script-location

format: ## Format
	python -m black *.py --exclude .venv/
	python -m isort *.py --skip .venv/

