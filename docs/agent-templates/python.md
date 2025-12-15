# Python Language - Agent Context Sections

> Sections to include when generating agent context files for Python projects.

## Quick Start Section

```markdown
## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
{{ test_command }}

# Run linting
{{ lint_command }}
```
```

## Code Style Section

```markdown
## Code Style

### Formatting & Linting

- **Formatter**: {{ formatter }} ({{ formatter_config }})
- **Linter**: {{ linter }} with {{ linter_config }}
- **Type checker**: {{ type_checker }}

### Type Hints

All public functions must have type hints:

```python
# Good
def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
    ...

# Bad - missing types
def process_data(items, limit=10):
    ...
```

### Docstrings

Use Google-style docstrings for public APIs:

```python
def create_resource(name: str, options: dict | None = None) -> Resource:
    """Create a new resource with the given name.

    Args:
        name: Unique identifier for the resource
        options: Optional configuration dictionary

    Returns:
        The created Resource instance

    Raises:
        ValueError: If name is empty or contains invalid characters
        ResourceExistsError: If a resource with this name already exists
    """
```
```

## Testing Section

```markdown
## Testing Conventions

### Test File Naming

```
src/{{ package }}/module.py  →  tests/unit/test_module.py
src/{{ package }}/sub/thing.py  →  tests/unit/sub/test_thing.py
```

### Test Structure

```python
import pytest
from {{ package }}.module import function_under_test

class TestFunctionName:
    """Tests for function_under_test."""

    def test_returns_expected_result(self):
        """Should return X when given Y."""
        result = function_under_test(input_value)
        assert result == expected_value

    def test_handles_edge_case(self):
        """Should handle empty input gracefully."""
        result = function_under_test([])
        assert result == default_value

    def test_raises_on_invalid_input(self):
        """Should raise ValueError for invalid input."""
        with pytest.raises(ValueError, match="must be positive"):
            function_under_test(-1)
```

### Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value", "items": [1, 2, 3]}

@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("setting: value")
    return config_file
```

### Mocking

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    """Test using mocked dependency."""
    with patch("{{ package }}.module.external_service") as mock:
        mock.return_value = {"status": "ok"}
        result = function_that_uses_service()
        mock.assert_called_once_with(expected_args)
```
```

## Error Handling Section

```markdown
## Error Handling

### Custom Exceptions

Define exceptions in `{{ package }}/exceptions.py`:

```python
class {{ ProjectName }}Error(Exception):
    """Base exception for {{ project_name }}."""
    pass

class ConfigurationError({{ ProjectName }}Error):
    """Raised when configuration is invalid."""
    pass

class ResourceNotFoundError({{ ProjectName }}Error):
    """Raised when a requested resource doesn't exist."""
    pass
```

### Error Patterns

```python
# Good - specific exception with context
if not path.exists():
    raise FileNotFoundError(f"Config file not found: {path}")

# Good - chain exceptions to preserve context
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    raise ConfigurationError(f"Invalid JSON in {path}") from e

# Bad - bare exception
try:
    risky_operation()
except Exception:
    pass  # Silent failure - never do this
```
```

## Security Section

```markdown
## Security Considerations

### Input Validation

```python
import re

def validate_name(name: str) -> str:
    """Validate and sanitize a name input."""
    if not name or len(name) > 100:
        raise ValueError("Name must be 1-100 characters")

    # Only allow alphanumeric, dash, underscore
    if not re.match(r'^[\w\-]+$', name):
        raise ValueError("Name contains invalid characters")

    return name
```

### Path Safety

```python
from pathlib import Path

def safe_join(base: Path, user_path: str) -> Path:
    """Safely join paths, preventing directory traversal."""
    # Resolve to absolute path
    result = (base / user_path).resolve()

    # Verify still within base
    if not result.is_relative_to(base.resolve()):
        raise ValueError("Path traversal detected")

    return result
```

### Secrets

```python
# CORRECT - Use environment or keyring
import keyring
api_key = keyring.get_password("service", "api_key")

# WRONG - Never hardcode or log secrets
api_key = "sk-secret-key"  # Never do this
logger.info(f"Using key: {api_key}")  # Never log secrets
```
```

## Dependencies Section

```markdown
## Dependencies

### Adding Dependencies

1. Add to `pyproject.toml`:
   - Runtime deps: `[project.dependencies]`
   - Dev deps: `[project.optional-dependencies].dev`

2. Pin major version only: `requests>=2.28,<3`

3. Update environment: `pip install -e ".[dev]"`

### Import Order

```python
# Standard library
import os
from pathlib import Path

# Third-party
import click
import requests

# Local
from {{ package }}.config import settings
from {{ package }}.utils import helper
```
```

## Gotchas Section

```markdown
## Python-Specific Gotchas

1. **Mutable default arguments**:
   ```python
   # WRONG
   def append_item(item, items=[]):
       items.append(item)
       return items

   # CORRECT
   def append_item(item, items=None):
       if items is None:
           items = []
       items.append(item)
       return items
   ```

2. **Late binding in closures**:
   ```python
   # WRONG - all functions return 4
   funcs = [lambda: i for i in range(5)]

   # CORRECT - capture value
   funcs = [lambda i=i: i for i in range(5)]
   ```

3. **String formatting with untrusted input**:
   ```python
   # WRONG - format string attack
   template = user_input
   result = template.format(secret=secret_value)

   # CORRECT - use safe formatting
   result = f"Hello, {escape(user_input)}"
   ```

4. **Circular imports**: Use TYPE_CHECKING for type-only imports:
   ```python
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from {{ package }}.other import OtherClass
   ```
```
