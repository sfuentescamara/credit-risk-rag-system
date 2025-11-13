.PHONY: help install install-dev test lint format clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make type-check    - Run type checking"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make docker-up     - Start Docker services"
	@echo "  make docker-down   - Stop Docker services"
	@echo "  make pre-commit    - Run pre-commit hooks"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing tests/

lint:
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

type-check:
	mypy src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

pre-commit:
	pre-commit run --all-files

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
