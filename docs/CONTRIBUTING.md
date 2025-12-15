# Contributing to SpecInit

Thank you for your interest in contributing to SpecInit! This guide will help you get started quickly and ensure your contributions align with the project's standards.

---

## Quick Reference

```bash
# Setup (one-time)
git clone https://github.com/Geoffe-Ga/specinit.git && cd specinit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# Daily workflow
./scripts/test.sh           # Run all tests
./scripts/lint.sh           # Run all linters
pre-commit run --all-files  # Run all checks
```

---

## Development Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Runtime |
| Node.js | 18+ | Frontend development |
| Git | Latest | Version control |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Geoffe-Ga/specinit.git
cd specinit

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies (includes dev tools)
pip install -e ".[dev]"

# 4. Set up pre-commit hooks
pre-commit install

# 5. Verify setup
./scripts/test.sh           # All tests should pass
./scripts/lint.sh           # No errors
```

### Frontend Setup (Optional)

Only needed if working on the web UI:

```bash
cd frontend
npm install
npm run dev    # Starts dev server at http://localhost:5173
```

---

## Project Architecture

Understanding the codebase helps you contribute effectively.

### Directory Structure

```
specinit/
├── src/specinit/              # Main Python package
│   ├── cli/                   # Click CLI commands
│   │   └── main.py            # Entry point: init, new, list, config
│   ├── server/                # FastAPI web server
│   │   ├── app.py             # HTTP routes + WebSocket
│   │   └── static/            # Built frontend (generated)
│   ├── generator/             # Core generation logic
│   │   ├── orchestrator.py    # 8-step generation coordinator
│   │   ├── prompts.py         # Claude prompt templates
│   │   └── templates.py       # Built-in project templates
│   └── storage/               # Persistence layer
│       ├── config.py          # YAML config + keyring
│       └── history.py         # SQLite project history
├── frontend/                  # React + Vite + Tailwind
│   └── src/
│       ├── App.tsx            # Main component
│       └── components/        # Form wizard UI
├── tests/
│   ├── unit/                  # Isolated unit tests
│   ├── integration/           # End-to-end tests
│   └── conftest.py            # Shared fixtures
├── scripts/                   # Development scripts
│   ├── lint.sh                # Run all linters
│   └── test.sh                # Run all tests
└── docs/                      # Documentation
```

### Key Design Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| CLI Framework | Click | Industry standard, auto-generated help, command grouping |
| Web Framework | FastAPI | Async support, WebSocket for progress, auto-docs |
| Database | SQLite | Zero configuration, perfect for local-first apps |
| Secret Storage | Keyring | OS-native (Keychain/Credential Locker/Secret Service) |
| Testing | pytest | De facto standard, excellent fixture system |
| Linting | Ruff | Fast, replaces multiple tools (flake8, isort, etc.) |

### Data Flow

```
User runs `specinit new`
         │
         ▼
    CLI (main.py)
         │
         ├── Starts FastAPI server
         └── Opens browser to localhost:8000
                  │
                  ▼
         Frontend (React form wizard)
                  │
                  ├── WebSocket connection for progress
                  └── POST /generate with answers
                           │
                           ▼
                  Generator Orchestrator
                           │
                           ├── Step 1-4: Claude API calls
                           ├── Step 5-7: Local operations
                           └── Step 8: Claude API (demo code)
                                    │
                                    ▼
                           File Writer → Project Directory
```

---

## Making Changes

### Finding Something to Work On

1. **Good First Issues**: Look for issues labeled [`good first issue`](https://github.com/Geoffe-Ga/specinit/labels/good%20first%20issue)
2. **Bug Fixes**: Issues labeled [`bug`](https://github.com/Geoffe-Ga/specinit/labels/bug)
3. **Features**: Issues labeled [`enhancement`](https://github.com/Geoffe-Ga/specinit/labels/enhancement)
4. **Documentation**: Always welcome without prior discussion

### Workflow

```bash
# 1. Create a feature branch
git checkout -b feat/your-feature-name

# 2. Make changes (write tests first!)
# ... edit files ...

# 3. Run checks locally
./scripts/test.sh           # Must pass
./scripts/lint.sh           # Must pass
pre-commit run --all-files  # Must pass

# 4. Commit with conventional message
git add .
git commit -m "feat: add new template for Django projects"

# 5. Push and create PR
git push -u origin feat/your-feature-name
```

---

## Code Style

### Python

**Formatting**: Handled automatically by `ruff format`

**Type Hints**: Required for all public functions

```python
# CORRECT - explicit types
def generate_project(
    answers: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> GenerationResult:
    """Generate a project from user answers."""
    ...

# WRONG - missing types
def generate_project(answers, output_dir, dry_run=False):
    ...
```

**Docstrings**: Required for public APIs, Google style

```python
# CORRECT - Google style docstring
def create_resource(name: str, options: dict | None = None) -> Resource:
    """Create a new resource with the given name.

    Args:
        name: Unique identifier for the resource.
        options: Optional configuration dictionary.

    Returns:
        The created Resource instance.

    Raises:
        ValueError: If name is empty or contains invalid characters.
        ResourceExistsError: If a resource with this name already exists.
    """
```

**Error Handling**: Use custom exceptions, preserve context

```python
# CORRECT - specific exception with context
try:
    config = load_config(path)
except FileNotFoundError:
    raise ConfigurationError(f"Config file not found: {path}") from None

# WRONG - swallowing errors
try:
    config = load_config(path)
except Exception:
    pass  # Never do this
```

### TypeScript/React

- **Functional components** with hooks (no class components)
- **TypeScript strict mode** enabled
- **Named exports** preferred over default exports

```tsx
// CORRECT - functional component with types
interface UserCardProps {
  user: User;
  onSelect?: (user: User) => void;
}

export function UserCard({ user, onSelect }: UserCardProps) {
  return (
    <div onClick={() => onSelect?.(user)}>
      <h3>{user.name}</h3>
    </div>
  );
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new template for Django projects
fix: resolve API key encryption on Windows
docs: update installation instructions
test: add integration tests for generator
refactor: simplify cost calculation logic
chore: update dependencies
```

---

## Testing

### Running Tests

```bash
# All tests
./scripts/test.sh

# With coverage report
pytest --cov=src/specinit --cov-report=html

# Specific file
pytest tests/unit/test_cli.py

# Specific test
pytest tests/unit/test_cli.py::TestInitCommand::test_stores_api_key

# Watch mode (requires pytest-watch)
ptw
```

### Writing Tests

**Naming**: Test files mirror source files

```
src/specinit/generator/orchestrator.py
  → tests/unit/test_orchestrator.py
```

**Structure**: Use descriptive class and method names

```python
class TestGenerateProject:
    """Tests for generate_project function."""

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        """Should create output directory if it doesn't exist."""
        output_dir = tmp_path / "new-project"

        generate_project(valid_answers, output_dir)

        assert output_dir.exists()

    def test_raises_on_existing_directory(self, tmp_path: Path) -> None:
        """Should raise if output directory already exists."""
        output_dir = tmp_path / "existing"
        output_dir.mkdir()

        with pytest.raises(ProjectExistsError, match="already exists"):
            generate_project(valid_answers, output_dir)
```

**Fixtures**: Use pytest fixtures for test data

```python
@pytest.fixture
def valid_answers() -> dict[str, Any]:
    """Provide valid project generation answers."""
    return {
        "platforms": ["web"],
        "user_story": "As a user, I want to...",
        "features": ["Feature 1", "Feature 2"],
        "tech_stack": {"frontend": "react", "backend": "fastapi"},
        "aesthetic": "minimalist",
    }
```

**Mocking**: Mock external dependencies (API calls, file system)

```python
def test_generates_with_claude(self, mock_anthropic: MagicMock) -> None:
    """Should call Claude API with correct prompt."""
    mock_anthropic.messages.create.return_value = MockResponse(content="...")

    generate_project(valid_answers, output_dir)

    mock_anthropic.messages.create.assert_called_once()
```

### Coverage Requirements

- **Target**: 80%+ coverage on core logic
- **Required**: All new code must have tests
- **CI**: Coverage check runs automatically on PRs

---

## Common Tasks

### Adding a New Template

1. **Edit `src/specinit/generator/templates.py`**:
   ```python
   TEMPLATES["django"] = {
       "name": "django",
       "description": "Django web application",
       "platforms": ["web"],
       "tech_stack": {
           "backend": "django",
           "database": "postgresql",
       },
       "directory_structure": {
           "src/": {...},
           "tests/": {...},
       },
   }
   ```

2. **Add tests in `tests/unit/test_templates.py`**

3. **Update documentation** if needed

### Adding a CLI Command

1. **Add to `src/specinit/cli/main.py`**:
   ```python
   @cli.command()
   @click.argument("name")
   def new_command(name: str) -> None:
       """Short description of command."""
       ...
   ```

2. **Add tests in `tests/unit/test_cli.py`**

### Modifying Claude Prompts

1. **Edit `src/specinit/generator/prompts.py`**

2. **Test with sample generation** - prompts significantly affect output quality

3. **Document changes** in PR description

---

## Debugging Tips

### Common Issues

| Issue | Solution |
|-------|----------|
| `keyring.errors.NoKeyringError` | Install system keyring backend (see [keyring docs](https://pypi.org/project/keyring/)) |
| WebSocket connection fails | Clear browser cache, check port 8000 is free |
| Tests fail on CI but pass locally | Check for filesystem/OS-specific behavior |
| Import errors after install | Run `pip install -e ".[dev]"` again |

### Debugging Commands

```bash
# Check installed version
pip show specinit

# Run with verbose output
specinit --verbose new

# Check configuration
specinit config show

# Run single test with output
pytest -vvs tests/unit/test_cli.py::test_name
```

---

## Pull Request Process

### Before Submitting

1. **All checks pass locally**:
   ```bash
   ./scripts/test.sh
   ./scripts/lint.sh
   pre-commit run --all-files
   ```

2. **Tests added** for new functionality

3. **Documentation updated** if behavior changes

### PR Description Template

```markdown
## Summary

Brief description of changes.

## Changes

- Added X
- Fixed Y
- Updated Z

## Testing

How to test these changes manually (if applicable).

## Checklist

- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Documentation updated
```

### Review Process

1. **Automated checks** run on PR creation
2. **Code review** by maintainer
3. **Address feedback** with additional commits
4. **Squash merge** when approved

---

## Getting Help

- **Bug reports**: [Open an issue](https://github.com/Geoffe-Ga/specinit/issues/new?template=bug_report.md)
- **Feature requests**: [Open an issue](https://github.com/Geoffe-Ga/specinit/issues/new?template=feature_request.md)
- **Questions**: [Start a discussion](https://github.com/Geoffe-Ga/specinit/discussions)
- **Security issues**: Email security@specinit.dev (do not open public issues)

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](../LICENSE).
