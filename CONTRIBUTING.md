# Contributing Guidelines

## Code Style

- Use `black` for formatting
- Use `ruff` for linting
- Maximum line length: 100 characters
- Type hints recommended for public APIs

## Testing

All code should be tested:

```bash
pytest --cov=devops_ai
```

Minimum coverage: 80%

## Commit Messages

Follow conventional commits:

```
feat: add new terraform generator
fix: resolve config loading issue
docs: update README with examples
test: add tests for kubernetes generator
```

## Pull Requests

1. Create a feature branch
2. Make atomic commits
3. Add tests for new features
4. Update documentation
5. Submit PR with clear description
