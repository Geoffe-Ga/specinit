{# README Template for SpecInit-Generated Projects #}
{# Uses Jinja2 syntax for dynamic content #}

<p align="center">
  <img src="docs/assets/logo.png" alt="{{ project_name }} Logo" width="120" />
</p>

<h1 align="center">{{ project_name }}</h1>

<p align="center">
  <strong>{{ tagline }}</strong>
</p>

<p align="center">
  <a href="https://github.com/{{ github_username }}/{{ project_slug }}/actions/workflows/ci.yml">
    <img src="https://github.com/{{ github_username }}/{{ project_slug }}/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-{{ license }}-blue.svg" alt="License" />
  </a>
  {% if language == 'python' %}
  <a href="https://pypi.org/project/{{ project_slug }}/">
    <img src="https://img.shields.io/pypi/v/{{ project_slug }}.svg" alt="PyPI Version" />
  </a>
  {% elif language == 'typescript' %}
  <a href="https://www.npmjs.com/package/{{ project_slug }}">
    <img src="https://img.shields.io/npm/v/{{ project_slug }}.svg" alt="npm Version" />
  </a>
  {% endif %}
</p>

---

## The Problem

{{ problem_statement }}

**{{ project_name }} solves this.**

{{ solution_summary }}

---

## Demo

<p align="center">
  <img src="docs/assets/demo.gif" alt="{{ project_name }} Demo" width="600" />
</p>

```{{ shell_lang }}
{{ demo_command_output }}
```

---

## Quick Start

```{{ shell_lang }}
# Install {{ project_name }}
{{ install_command }}

{% if has_config %}
# Configure (if needed)
{{ config_command }}

{% endif %}
# Run
{{ run_command }}
```

{% if quick_start_notes %}
{{ quick_start_notes }}
{% endif %}

---

## Features

{% for feature in features %}
- **{{ feature.name }}** - {{ feature.description }}
{% endfor %}

---

## Architecture

> For AI assistants: This section explains the codebase structure and design decisions.

### Project Structure

```
{{ project_structure }}
```

### Key Components

| Component | Purpose |
|-----------|---------|
{% for component in components %}
| `{{ component.path }}` | {{ component.description }} |
{% endfor %}

{% if design_decisions %}
### Design Decisions

| Decision | Rationale |
|----------|-----------|
{% for decision in design_decisions %}
| {{ decision.what }} | {{ decision.why }} |
{% endfor %}
{% endif %}

{% if data_flow %}
### Data Flow

```
{{ data_flow }}
```
{% endif %}

---

{% if has_cli %}
## CLI Reference

```{{ shell_lang }}
{% for cmd in cli_commands %}
{{ project_slug }} {{ cmd.name }}{{ '  ' }}# {{ cmd.description }}
{% endfor %}
```

---

{% endif %}

{% if has_api %}
## API Reference

{% if api_docs_url %}
Full API documentation available at `{{ api_docs_url }}` when running.
{% endif %}

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
{% for endpoint in api_endpoints %}
| `{{ endpoint.method }}` | `{{ endpoint.path }}` | {{ endpoint.description }} |
{% endfor %}

---

{% endif %}

## Configuration

{% if config_file_path %}
**Config location:** `{{ config_file_path }}`

```{{ config_format }}
{{ config_example }}
```
{% endif %}

{% if env_vars %}
**Environment variables:**
{% for var in env_vars %}
- `{{ var.name }}` - {{ var.description }}{% if var.required %} (required){% endif %}

{% endfor %}
{% endif %}

---

## Development

### Prerequisites

{% for prereq in prerequisites %}
- {{ prereq.name }} {{ prereq.version }}{% if prereq.purpose %} ({{ prereq.purpose }}){% endif %}

{% endfor %}

### Setup

```{{ shell_lang }}
# Clone the repository
git clone {{ repo_url }}
cd {{ project_slug }}

# Install dependencies
{{ dev_install_command }}

# Run tests
{{ test_command }}

# Run linting
{{ lint_command }}
```

{% if has_frontend %}
### Frontend Development

```{{ shell_lang }}
cd frontend
{{ frontend_install_command }}
{{ frontend_run_command }}
```
{% endif %}

---

{% if security_notes %}
## Security

{{ security_notes }}

{% endif %}

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Development setup
- Testing guidelines
- Code style requirements
- Pull request process

---

## License

{{ license }} License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Generated with <a href="https://github.com/specinit/specinit">SpecInit</a></sub>
</p>
