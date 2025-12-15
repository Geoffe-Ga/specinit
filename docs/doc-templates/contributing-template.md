{# CONTRIBUTING Template for SpecInit-Generated Projects #}
{# Uses Jinja2 syntax for dynamic content #}

# Contributing to {{ project_name }}

Thank you for your interest in contributing to {{ project_name }}! This guide will help you get started quickly.

---

## Quick Reference

```{{ shell_lang }}
# Setup (one-time)
git clone {{ repo_url }} && cd {{ project_slug }}
{{ dev_install_command }}
{% if has_pre_commit %}
pre-commit install
{% endif %}

# Daily workflow
{{ test_command }}{{ '           ' }}# Run all tests
{{ lint_command }}{{ '           ' }}# Run all linters
{% if has_pre_commit %}
pre-commit run --all-files  # Run all checks
{% endif %}
```

---

## Development Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
{% for prereq in prerequisites %}
| {{ prereq.name }} | {{ prereq.version }} | {{ prereq.purpose }} |
{% endfor %}

### Installation

```{{ shell_lang }}
# 1. Clone the repository
git clone {{ repo_url }}
cd {{ project_slug }}

{% if language == 'python' %}
# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies (includes dev tools)
pip install -e ".[dev]"
{% elif language == 'typescript' %}
# 2. Install dependencies
{{ package_manager }} install
{% endif %}

{% if has_pre_commit %}
# {{ step_number }}. Set up pre-commit hooks
pre-commit install
{% endif %}

# Verify setup
{{ test_command }}  # All tests should pass
{{ lint_command }}  # No errors
```

{% if has_frontend %}
### Frontend Setup

Only needed if working on the web UI:

```{{ shell_lang }}
cd frontend
{{ frontend_install_command }}
{{ frontend_run_command }}
```
{% endif %}

---

## Project Architecture

### Directory Structure

```
{{ project_structure }}
```

{% if key_files %}
### Key Files

| File | Purpose |
|------|---------|
{% for file in key_files %}
| `{{ file.path }}` | {{ file.description }} |
{% endfor %}
{% endif %}

{% if design_decisions %}
### Design Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
{% for decision in design_decisions %}
| {{ decision.component }} | {{ decision.choice }} | {{ decision.rationale }} |
{% endfor %}
{% endif %}

---

## Making Changes

### Finding Something to Work On

1. **Good First Issues**: Look for issues labeled [`good first issue`]({{ repo_url }}/labels/good%20first%20issue)
2. **Bug Fixes**: Issues labeled [`bug`]({{ repo_url }}/labels/bug)
3. **Features**: Issues labeled [`enhancement`]({{ repo_url }}/labels/enhancement)
4. **Documentation**: Always welcome without prior discussion

### Workflow

```{{ shell_lang }}
# 1. Create a feature branch
git checkout -b feat/your-feature-name

# 2. Make changes (write tests first!)
# ... edit files ...

# 3. Run checks locally
{{ test_command }}{{ '           ' }}# Must pass
{{ lint_command }}{{ '           ' }}# Must pass
{% if has_pre_commit %}
pre-commit run --all-files  # Must pass
{% endif %}

# 4. Commit with conventional message
git add .
git commit -m "feat: description of your changes"

# 5. Push and create PR
git push -u origin feat/your-feature-name
```

---

## Code Style

{% if language == 'python' %}
### Python

**Formatting**: Handled automatically by `{{ formatter }}`

**Type Hints**: Required for all public functions

```python
# CORRECT - explicit types
def process_data(
    items: list[str],
    limit: int = 10,
) -> dict[str, int]:
    """Process items and return counts."""
    ...

# WRONG - missing types
def process_data(items, limit=10):
    ...
```

**Docstrings**: Required for public APIs, Google style

```python
def create_resource(name: str, options: dict | None = None) -> Resource:
    """Create a new resource with the given name.

    Args:
        name: Unique identifier for the resource.
        options: Optional configuration dictionary.

    Returns:
        The created Resource instance.

    Raises:
        ValueError: If name is empty or invalid.
    """
```
{% elif language == 'typescript' %}
### TypeScript

**Formatting**: Handled automatically by `{{ formatter }}`

**Type Annotations**: Required for all exports

```typescript
// CORRECT - explicit types
export function processData(
  items: string[],
  options?: ProcessOptions
): Record<string, number> {
  // ...
}

// WRONG - implicit any
export function processData(items, options) {
  // ...
}
```

**Interfaces**: Prefer interfaces over type aliases for objects

```typescript
// Preferred
interface User {
  id: string;
  name: string;
  email: string;
}

// Use type for unions/intersections
type Status = 'pending' | 'active' | 'completed';
```
{% endif %}

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: resolve bug in X
docs: update installation instructions
test: add tests for Y
refactor: simplify Z logic
chore: update dependencies
```

---

## Testing

### Running Tests

```{{ shell_lang }}
# All tests
{{ test_command }}

# With coverage report
{{ coverage_command }}

# Specific file
{{ test_single_file_command }}

# Specific test
{{ test_single_test_command }}
```

### Writing Tests

**Naming**: Test files mirror source files

```
{{ test_file_convention }}
```

**Structure**: Use descriptive names

```{{ language }}
{{ test_example }}
```

### Coverage Requirements

- **Target**: {{ coverage_target }}% coverage on core logic
- **Required**: All new code must have tests
- **CI**: Coverage check runs automatically on PRs

---

## Common Tasks

{% for task in common_tasks %}
### {{ task.name }}

{{ task.description }}

{% if task.steps %}
{% for step in task.steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
{% endif %}

{% if task.code %}
```{{ task.code_lang }}
{{ task.code }}
```
{% endif %}

{% endfor %}

---

## Debugging Tips

### Common Issues

| Issue | Solution |
|-------|----------|
{% for issue in common_issues %}
| {{ issue.problem }} | {{ issue.solution }} |
{% endfor %}

### Useful Commands

```{{ shell_lang }}
{% for cmd in debug_commands %}
{{ cmd.command }}{{ '  ' }}# {{ cmd.description }}
{% endfor %}
```

---

## Pull Request Process

### Before Submitting

1. **All checks pass locally**:
   ```{{ shell_lang }}
   {{ test_command }}
   {{ lint_command }}
   {% if has_pre_commit %}
   pre-commit run --all-files
   {% endif %}
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

- **Bug reports**: [Open an issue]({{ repo_url }}/issues/new?template=bug_report.md)
- **Feature requests**: [Open an issue]({{ repo_url }}/issues/new?template=feature_request.md)
- **Questions**: [Start a discussion]({{ repo_url }}/discussions)

---

## License

By contributing, you agree that your contributions will be licensed under the [{{ license }} License](../LICENSE).
