# Credit Risk RAG System

A sophisticated Credit Risk Assessment System powered by Retrieval-Augmented Generation (RAG) technology, combining traditional credit risk analysis with advanced Large Language Models (LLMs).

## Overview

This system leverages RAG architecture to provide intelligent credit risk assessments by:
- Retrieving relevant historical credit data and regulations
- Augmenting LLM responses with domain-specific knowledge
- Generating comprehensive risk analysis reports
- Providing explainable AI-driven credit decisions

## Features

- **RAG-Powered Risk Analysis**: Combines vector similarity search with LLM generation
- **Real-time Credit Assessment**: Fast API endpoints for credit evaluation
- **Document Understanding**: Process and analyze financial documents
- **Explainable AI**: Transparent reasoning for credit decisions
- **Scalable Architecture**: Microservices design with Docker support
- **Async Processing**: Celery-based task queue for batch operations
- **Vector Search**: ChromaDB integration for semantic document retrieval
- **API-First Design**: RESTful API with FastAPI

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  RAG Engine  │────▶│   ChromaDB  │
│     API     │     │              │     │   (Vector)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │
       │                    ▼
       │            ┌──────────────┐
       │            │   LLM/OpenAI │
       │            └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  PostgreSQL │     │    Redis     │
│  (Database) │     │   (Cache)    │
└─────────────┘     └──────────────┘
```

## Project Structure

```
credit-risk-rag-system/
├── src/
│   ├── api/              # FastAPI application
│   ├── rag/              # RAG engine and retrieval logic
│   ├── llm/              # LLM integration and prompts
│   ├── analyzer/         # Credit risk analysis logic
│   ├── data/             # Data models and database
│   └── __init__.py
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── docker-compose.yml    # Docker services
├── Dockerfile.dev        # Development Dockerfile
├── pyproject.toml        # Project configuration
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+
- OpenAI API key (or compatible LLM API)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sfuentescamara/credit-risk-rag-system.git
cd credit-risk-rag-system
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Set your OPENAI_API_KEY
nano .env
```

### 3. Development Environment (Docker)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8000`

### 4. Local Development (Virtual Environment)

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run the application
uvicorn api.main:app --reload
```

## Development

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks for automatic checks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit
pytest tests/integration
```

### Code Formatting

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Type checking
mypy src
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## API Documentation

Once the application is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Configuration

Configuration is managed through environment variables (see `.env.example`):

- **Database**: PostgreSQL connection settings
- **Redis**: Cache and task queue configuration
- **ChromaDB**: Vector store settings
- **OpenAI**: API key and model selection
- **Application**: Port, host, logging levels

## Deployment

### Production Dockerfile

```bash
# Build production image
docker build -t credit-risk-rag-system:latest .

# Run production container
docker run -p 8000:8000 --env-file .env credit-risk-rag-system:latest
```

### Environment Variables

Ensure all required environment variables are set in production:
- `OPENAI_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Write type hints for all functions
- Add docstrings to public functions and classes
- Maintain test coverage above 80%
- Ensure all pre-commit hooks pass

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- RAG powered by [LangChain](https://langchain.com/)
- Vector search with [ChromaDB](https://www.trychroma.com/)
- LLM integration via [OpenAI](https://openai.com/)

## Support

For issues, questions, or contributions, please visit:
- **Issues**: https://github.com/sfuentescamara/credit-risk-rag-system/issues
- **Discussions**: https://github.com/sfuentescamara/credit-risk-rag-system/discussions

## Roadmap

- [ ] Enhanced credit scoring algorithms
- [ ] Multi-modal document analysis (PDFs, images)
- [ ] Real-time monitoring dashboard
- [ ] Integration with external credit bureaus
- [ ] Advanced explainability features
- [ ] Multi-language support
- [ ] REST and GraphQL APIs
