# Contributing to Credit Risk RAG System

Thank you for your interest in contributing to the Credit Risk RAG System!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/credit-risk-rag-system.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up development environment: `./scripts/setup-dev.sh`

## Development Workflow

### Code Standards

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for public functions and classes
- Keep functions small and focused (max 50 lines)
- Maintain test coverage above 80%

### Before Committing

1. **Run tests**: `make test-cov`
2. **Format code**: `make format`
3. **Run linters**: `make lint`
4. **Type check**: `make type-check`
5. **Pre-commit hooks**: Will run automatically on commit

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(rag): add document chunking with overlap

Implement sliding window chunking for better context preservation
in RAG retrieval.

Closes #123
```

### Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

### Code Review Checklist

- [ ] Code follows project style guide
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Security best practices followed
- [ ] Performance impact considered

## Testing

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names: `test_should_return_error_when_invalid_input`
- Follow AAA pattern: Arrange, Act, Assert

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test
pytest tests/unit/test_rag.py::test_chunking
```

## Documentation

- Update README.md for user-facing changes
- Update docs/ for architecture or API changes
- Add docstrings to all public functions
- Include examples in docstrings

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
