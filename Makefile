.DEFAULT_GOAL := help
.PHONY: install-dev install-client install-server format server client

### QUICK
# ¯¯¯¯¯¯¯

install-dev: ## Install dev dependencies
	pip install -r requirements-dev.txt --upgrade --no-warn-script-location

install-client: ## Install client dependencies
	pip install -r requirements-client.txt --upgrade --no-warn-script-location

install-server: ## Install server dependencies
	pip install -r requirements-server.txt --upgrade --no-warn-script-location

format: ## Format
	python -m black *.py --exclude .venv/
	python -m isort *.py --skip .venv/

server: ## Build and deploy server
	docker build --tag face-detection-demo .
	docker run -it -p 8765:8765 face-detection-demo:latest

client: ## Deploy client
	python client.py
