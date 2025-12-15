# Documentation Templates

This directory contains templates for generating README.md and CONTRIBUTING.md files in SpecInit-generated projects.

## Purpose

When SpecInit generates a new project, it creates documentation that is:
1. **Agent-optimized** - Structured for AI assistants to understand the project
2. **Human-friendly** - Visually appealing and easy to navigate
3. **Project-specific** - Populated with actual project details from user answers

## How SpecInit Uses These Templates

1. SpecInit reads the template files (`readme-template.md`, `contributing-template.md`)
2. Combines with language-specific sections from `../agent-templates/`
3. Populates placeholders with project-specific details
4. Writes final files to generated project's `docs/` directory

## Template Files

| File | Purpose |
|------|---------|
| `readme-template.md` | Base template for generated project READMEs |
| `contributing-template.md` | Base template for generated CONTRIBUTING guides |

## Placeholder Syntax

Templates use Jinja2 syntax for dynamic content:

```markdown
# {{ project_name }}

{{ project_description }}

## Quick Start

```bash
{{ install_command }}
{{ run_command }}
```
```

## Available Variables

### Project Information

| Variable | Source | Example |
|----------|--------|---------|
| `project_name` | User input / derived | `TimeTracker` |
| `project_slug` | Generated from name | `timetracker` |
| `project_description` | Generated from spec | `A time tracking app for...` |
| `version` | Default | `0.1.0` |

### Tech Stack

| Variable | Source | Example |
|----------|--------|---------|
| `language` | Template selection | `python` / `typescript` |
| `framework` | Template selection | `fastapi` / `react` |
| `package_manager` | Derived from language | `pip` / `npm` |
| `test_framework` | Derived from stack | `pytest` / `vitest` |

### Commands

| Variable | Derived From | Example |
|----------|--------------|---------|
| `install_command` | Package manager | `pip install -e ".[dev]"` |
| `run_command` | Framework | `python -m timetracker` |
| `test_command` | Test framework | `pytest` |
| `lint_command` | Linter config | `ruff check .` |

### Structure

| Variable | Generated | Example |
|----------|-----------|---------|
| `project_structure` | Directory tree | ASCII tree representation |
| `feature_list` | User input | List of features |
| `platforms` | User input | `["web", "mobile"]` |

## Conditional Sections

Templates support conditional rendering:

```markdown
{% if has_frontend %}
## Frontend Development

```bash
cd frontend
{{ frontend_install_command }}
{{ frontend_run_command }}
```
{% endif %}

{% if has_api %}
## API Documentation

API docs available at `http://localhost:8000/docs` when running.
{% endif %}
```

## Best Practices for Templates

### Structure for Agents

1. **Machine-readable sections** - Use consistent headers
2. **Quick reference table** - Commands at the top
3. **Architecture section** - For understanding the codebase
4. **Explicit file references** - Point to key files

### Structure for Humans

1. **Visual appeal** - Badges, logo placeholder, clean formatting
2. **Problem statement** - Why this project exists
3. **Demo section** - GIF/screenshot placeholder
4. **Zero-friction start** - Minimal steps to running

### Content Guidelines

1. **Actionable commands** - Copy-paste ready
2. **Specific examples** - Real code, not pseudocode
3. **Failure modes** - Common errors and solutions
4. **No assumptions** - Explain project-specific decisions

## Contributing

When modifying templates:

1. Update the template file
2. Test by generating a sample project
3. Verify both agent readability and human appeal
4. Update this README if adding new variables
