# FastCP Development Makefile

.PHONY: help install dev-server test lint format clean docker-build docker-up docker-down docker-logs dev-utils setup status

# Default target
help:
	@echo "FastCP Development Commands:"
	@echo ""
	@echo "Installation & Setup:"
	@echo "  install         Install Python and Node.js dependencies"
	@echo "  setup           Set up complete development environment"
	@echo "  migrate         Run Django migrations"
	@echo "  collectstatic   Collect Django static files"
	@echo ""
	@echo "Development:"
	@echo "  dev-server      Run development server on port 8899"
	@echo "  shell           Open Django shell"
	@echo "  dbshell         Open database shell"
	@echo "  status          Show project status"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test            Run all tests"
	@echo "  lint            Run code linting (flake8)"
	@echo "  format          Format code with black and isort"
	@echo "  quality         Run all quality checks"
	@echo "  security        Run security scan (bandit)"
	@echo "  safety          Check for vulnerable dependencies"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-up       Start Docker containers"
	@echo "  docker-down     Stop Docker containers"
	@echo "  docker-logs     Show Docker logs"
	@echo "  docker-shell    Open shell in Docker container"
	@echo ""
	@echo "Utilities:"
	@echo "  dev-utils       Run development utilities script"
	@echo "  clean           Remove Python and Node.js cache files"
	@echo "  clean-all       Remove all cache, build, and temp files"

# Installation
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Node.js dependencies..."
	npm install

setup:
	python dev_utils.py setup

migrate:
	python manage.py migrate

collectstatic:
	python manage.py collectstatic --noinput

# Development
dev-server:
	python run_dev.py

shell:
	python manage.py shell

dbshell:
	python manage.py dbshell

status:
	python dev_utils.py status

# Testing & Quality
test:
	DJANGO_SETTINGS_MODULE=fastcp.settings IS_DEBUG=1 pytest tests.py --verbosity=2

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	python dev_utils.py format

quality:
	python dev_utils.py quality

security:
	bandit -r . -f json -o security_report.json

safety:
	safety check --json > safety_report.json

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec fastcp bash

# Utilities
dev-utils:
	python dev_utils.py $(filter-out $@,$(MAKECMDGOALS))

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name ".cache" -exec rm -rf {} +

clean-all: clean
	rm -rf staticfiles/
	rm -rf logs/
	rm -rf tmp/
	rm -f db.sqlite3
	rm -f security_report.json
	rm -f safety_report.json
