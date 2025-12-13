# Contributing to SpecInit

Thank you for your interest in contributing to SpecInit! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend development)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/specinit/specinit.git
   cd specinit
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install frontend dependencies** (optional, for UI work):
   ```bash
   cd frontend
   npm install
   ```

5. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running the Application

**Backend only**:
```bash
specinit new --no-browser
```

**Frontend development** (with hot reload):
```bash
# Terminal 1: Start backend
specinit new --no-browser

# Terminal 2: Start frontend dev server
cd frontend
npm run dev
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/specinit --cov-report=html

# Specific test file
pytest tests/unit/test_cli.py

# Watch mode (requires pytest-watch)
ptw
```

### Code Quality

```bash
# Linting
ruff check src tests

# Type checking
mypy src

# Format code
ruff format src tests

# Run all checks (pre-commit)
pre-commit run --all-files
```

## Code Style

### Python

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting

### TypeScript/React

- Use functional components with hooks
- Use TypeScript strict mode
- Follow ESLint and Prettier configurations

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new template for FastAPI projects
fix: resolve API key encryption on Windows
docs: update installation instructions
test: add integration tests for generator
refactor: simplify cost calculation logic
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**:
   - Write tests first (TDD)
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

4. **Push and create PR**:
   ```bash
   git push -u origin feat/your-feature-name
   ```
   Then open a PR on GitHub.

5. **PR Requirements**:
   - All CI checks must pass
   - At least one approval required
   - Squash commits before merging

## Project Structure

```
specinit/
├── src/specinit/          # Python package
│   ├── cli/               # CLI commands (Click)
│   ├── server/            # FastAPI server
│   ├── generator/         # Generation logic
│   └── storage/           # Config & history
├── frontend/              # React application
│   └── src/
│       ├── components/    # UI components
│       └── pages/         # Page components
├── tests/
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
└── plan/                  # Project planning
```

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Mock external dependencies (API calls, file system)
- Aim for 80%+ coverage on core logic

### Integration Tests

- Test full generation flow
- Use temporary directories
- Mock Anthropic API for reproducibility

### Example Test

```python
def test_config_manager_stores_api_key(tmp_path, monkeypatch):
    """API key should be stored securely."""
    monkeypatch.setenv("HOME", str(tmp_path))

    config = ConfigManager()
    config.set_api_key("sk-ant-test-key")

    retrieved = config.get_api_key()
    assert retrieved == "sk-ant-test-key"
```

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
