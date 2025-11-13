# Development Guide

## Getting Started

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- Git
- OpenAI API key

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sfuentescamara/credit-risk-rag-system.git
   cd credit-risk-rag-system
   ```

2. **Set up virtual environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running Locally

```bash
# Start dependencies
docker-compose up -d postgres redis chromadb

# Run the application
uvicorn api.main:app --reload

# Run with debugger
python -m debugpy --listen 5678 -m uvicorn api.main:app --reload
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_rag.py
pytest -k "test_credit_score"

# Run with markers
pytest -m unit
pytest -m integration
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
flake8 src tests

# Type check
mypy src

# Run all checks
pre-commit run --all-files
```

## Project Structure

```
src/
├── api/              # API endpoints and routes
├── rag/              # RAG implementation
├── llm/              # LLM integration
├── analyzer/         # Risk analysis
└── data/             # Data models
```

## Adding New Features

1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Update documentation
5. Run code quality checks
6. Submit PR

## Debugging

### Using Python Debugger

```python
import pdb; pdb.set_trace()
```

### Using VS Code
Configure `.vscode/launch.json` for debugging FastAPI

### Logging
Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging

## Common Tasks

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Adding Dependencies

```bash
# Add to requirements.txt
echo "package>=version" >> requirements.txt

# Install
pip install -r requirements.txt
```

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check network connectivity

### ChromaDB Issues
- Ensure ChromaDB container is running
- Verify CHROMA_URL configuration
- Check authentication credentials

### OpenAI API Issues
- Verify API key is set
- Check rate limits
- Monitor API usage
