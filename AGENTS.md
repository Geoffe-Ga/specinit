# AGENTS.md - AI Agent Instructions for SpecInit

> This file provides context for AI coding assistants (OpenAI Codex, GitHub Copilot, Claude, Cursor, etc.) working on this codebase. It complements CLAUDE.md with a provider-agnostic format.

## Quick Reference

```
Language:    Python 3.11+
Framework:   FastAPI (backend), React (frontend)
Package:     pip install -e ".[dev]"
Test:        ./scripts/test.sh
Lint:        ./scripts/lint.sh
All checks:  pre-commit run --all-files
```

## Critical Rules

These rules are NON-NEGOTIABLE. Violating them will break the build or introduce bugs.

### 1. Never Take Shortcuts

```
NEVER do these:
- Comment out failing tests
- Add # noqa or # type: ignore without justification
- Relax linter rules to suppress errors
- Change assertions to match wrong behavior
- Skip pre-commit hooks

ALWAYS do these:
- Fix the root cause of failures
- Add tests for new functionality
- Run full test suite before committing
```

### 2. Use Project Scripts

```bash
# CORRECT - Use provided scripts
./scripts/lint.sh
./scripts/test.sh
pre-commit run --all-files

# WRONG - Don't run tools directly
python -m pytest tests/
python -m ruff check src/
ruff format src/
```

**Why?** Direct invocation may use system Python instead of the virtual environment, causing inconsistent results between local development and CI.

### 3. Work From Project Root

All commands assume execution from the repository root directory. Never `cd` into subdirectories to run commands.

```bash
# CORRECT
pytest tests/unit/test_cli.py

# WRONG
cd tests/unit && pytest test_cli.py
```

### 4. Efficient CI Monitoring

Do not use blocking `--watch` commands for CI checks. These waste resources and context.

```bash
# WRONG - Blocks indefinitely, wastes context
gh pr checks 21 --watch

# CORRECT - Check once without blocking
gh pr checks 21

# CORRECT - Check status and move on
gh pr view 21 --json statusCheckRollup
```

**CI monitoring guidelines:**
- Check CI status once after pushing, then proceed with other work
- If CI is still pending, check back after completing another task
- Never poll CI status repeatedly in a loop
- Trust that CI will complete; check the PR comments for review feedback

## Project Structure

```
specinit/
├── src/specinit/           # Main package
│   ├── cli/                # Click CLI commands
│   ├── server/             # FastAPI web server
│   ├── generator/          # Project generation logic
│   ├── github/             # GitHub integration
│   └── storage/            # Config and history persistence
├── frontend/               # React + Vite UI
├── tests/                  # pytest test suite
│   ├── unit/               # Unit tests
│   └── conftest.py         # Shared fixtures
├── scripts/                # Development scripts
└── templates/              # Project templates (Jinja2)
```

## Code Style

### Python

- **Formatter**: ruff format (line length 100)
- **Linter**: ruff check with strict rules
- **Type checker**: mypy in strict mode
- **Docstrings**: Google style, required for public APIs

```python
# Good
def create_project(name: str, template: str = "default") -> Path:
    """Create a new project from a template.

    Args:
        name: Project name (used for directory)
        template: Template identifier

    Returns:
        Path to created project directory

    Raises:
        ValueError: If name contains invalid characters
    """
    ...

# Bad - missing types, docstring
def create_project(name, template="default"):
    ...
```

### TypeScript/React (Frontend)

- **Formatter**: Prettier
- **Linter**: ESLint with React rules
- **Components**: Functional components with hooks
- **State**: React Hook Form for forms, local state otherwise

## Common Tasks

### Adding a New CLI Command

1. Add command function in `src/specinit/cli/main.py`
2. Register with `@cli.command()` decorator
3. Add tests in `tests/unit/test_cli.py`
4. Update help text and docstrings

### Adding a New API Endpoint

1. Add route in `src/specinit/server/app.py`
2. Define Pydantic models for request/response
3. Add tests in `tests/unit/test_server.py`
4. Update WebSocket handlers if real-time updates needed

### Modifying Project Generation

1. Update prompts in `src/specinit/generator/prompts.py`
2. Update orchestrator in `src/specinit/generator/orchestrator.py`
3. If new template files needed, add to `templates/`
4. Update cost estimates in `src/specinit/generator/cost.py`

## Testing Conventions

### Test File Naming

```
src/specinit/cli/main.py     →  tests/unit/test_cli.py
src/specinit/server/app.py   →  tests/unit/test_server.py
```

### Test Structure

```python
class TestFeatureName:
    """Tests for [feature description]."""

    def test_success_case(self):
        """Should [expected behavior] when [condition]."""
        ...

    def test_error_case(self):
        """Should raise [Error] when [condition]."""
        ...
```

### Fixtures

Use pytest fixtures from `conftest.py`:
- `temp_dir`: Temporary directory cleaned up after test
- `mock_home`: Mocked home directory for config isolation
- `_mock_home`: Same as mock_home (underscore prefix for unused)

## Error Handling

### User-Facing Errors

```python
# Good - clear message, actionable
if not config.get_api_key():
    console.print("[red]Error:[/red] No API key configured.")
    console.print("\nRun 'specinit init' to set up your API key first.")
    raise SystemExit(1)

# Bad - cryptic error
if not config.get_api_key():
    raise ValueError("Missing key")
```

### Internal Errors

```python
# Good - preserve context, log details
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise GenerationError(f"Failed to generate: {e}") from e
```

## Security Considerations

1. **API Keys**: Store in OS keyring, never in files or logs
2. **User Input**: Validate and sanitize project names, paths
3. **File Operations**: Use pathlib, validate paths are within expected directories
4. **Subprocess**: Never pass user input directly to shell commands

```python
# Good - safe path handling
project_path = base_dir / sanitize_name(user_input)
if not project_path.is_relative_to(base_dir):
    raise ValueError("Invalid path")

# Bad - path traversal vulnerability
project_path = base_dir / user_input  # user could pass "../../../etc"
```

## Dependencies

When adding dependencies:
1. Add to `pyproject.toml` under appropriate section
2. Pin major version only: `requests>=2.28,<3`
3. Dev dependencies go in `[project.optional-dependencies].dev`
4. Run `pip install -e ".[dev]"` to update environment

## Git Workflow

### Commit Messages

```
type: short description

Longer explanation if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Branch Naming

```
feat/add-github-integration
fix/api-key-validation
docs/update-readme
test/improve-coverage
```

## Debugging Tips

### Test Failures

```bash
# Run single test with verbose output
./scripts/test.sh tests/unit/test_cli.py::TestInitCommand::test_init_with_valid_api_key -v

# Show print statements
./scripts/test.sh -s

# Stop on first failure
./scripts/test.sh -x
```

### Import Errors

If imports fail, ensure:
1. Virtual environment is activated: `source .venv/bin/activate`
2. Package is installed in dev mode: `pip install -e ".[dev]"`
3. You're in the project root directory

### Lint Errors

```bash
# Auto-fix what can be fixed
source .venv/bin/activate && ruff check --fix src tests

# Format code
source .venv/bin/activate && ruff format src tests
```

## What NOT to Do

1. **Don't modify these files without discussion**: `pyproject.toml`, `.pre-commit-config.yaml`, CI workflows
2. **Don't add new dependencies** without checking for existing alternatives
3. **Don't skip type hints** for public APIs
4. **Don't catch broad exceptions** (`except Exception:`) without re-raising
5. **Don't hardcode paths** - use `pathlib` and config
6. **Don't store secrets** in code, config files, or environment variables - use keyring

## Getting Help

- Architecture questions: See `CLAUDE.md`
- API documentation: Docstrings in source code
- Template customization: See `templates/` directory
- CI/CD: See `.github/workflows/`
