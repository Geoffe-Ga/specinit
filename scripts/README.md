# SpecInit Development Scripts

A comprehensive collection of shell scripts for development workflow automation.
These scripts are designed to be adaptable across different project types (Python, TypeScript, React, etc.) and provide consistent tooling for AI-assisted development.

## Quick Start

```bash
# Initial setup
./scripts/setup.sh

# Run all checks (lint + test)
./scripts/check.sh

# Format code
./scripts/format.sh

# Clean artifacts
./scripts/clean.sh
```

## Scripts Overview

| Script | Purpose | Key Options |
|--------|---------|-------------|
| `setup.sh` | Initialize development environment | `--skip-venv`, `--skip-frontend`, `--ci` |
| `lint.sh` | Run linters (ruff, mypy, ESLint) | `--fix`, `--python`, `--frontend` |
| `test.sh` | Run tests with targeting support | `-k pattern`, `--failed`, `--no-cov` |
| `check.sh` | Run lint + test together | `--fix`, `--lint-only`, `--test-only` |
| `format.sh` | Auto-format code | `--check`, `--python`, `--frontend` |
| `clean.sh` | Remove build artifacts | `--all`, `--dry-run`, `--logs` |

## Common Options

All scripts support these common options:

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Show detailed output |
| `--quiet`, `-q` | Minimal output |
| `--help`, `-h` | Show help message |
| `--no-log` | Skip log file creation |

## Detailed Usage

### setup.sh - Environment Setup

Sets up the complete development environment.

```bash
# Full setup (venv, dependencies, pre-commit hooks)
./scripts/setup.sh

# CI mode (non-interactive)
./scripts/setup.sh --ci

# Skip specific steps
./scripts/setup.sh --skip-venv --skip-frontend
```

**What it does:**
1. Creates Python virtual environment
2. Installs Python dependencies from `pyproject.toml`
3. Installs frontend npm dependencies
4. Installs pre-commit hooks
5. Validates the setup

### lint.sh - Linting

Runs all configured linters.

```bash
# Check for issues
./scripts/lint.sh

# Auto-fix issues
./scripts/lint.sh --fix

# Python only
./scripts/lint.sh --python

# Frontend only
./scripts/lint.sh --frontend

# Specific paths
./scripts/lint.sh src/specinit/core
```

**Tools used:**
- **Python**: ruff check, ruff format --check, mypy
- **Frontend**: ESLint, TypeScript compiler

### test.sh - Testing

Runs tests with comprehensive targeting support.

```bash
# Run all tests
./scripts/test.sh

# Run specific file
./scripts/test.sh tests/unit/test_cli.py

# Run specific class
./scripts/test.sh tests/unit/test_cli.py::TestInitCommand

# Run specific test method
./scripts/test.sh tests/unit/test_cli.py::TestInitCommand::test_init

# Pattern matching (-k)
./scripts/test.sh -k "test_config"
./scripts/test.sh -k "config or settings"

# Run tests with specific marker (-m)
./scripts/test.sh -m "slow"
./scripts/test.sh -m "not integration"

# Re-run only failed tests
./scripts/test.sh --failed

# Skip coverage
./scripts/test.sh --no-cov

# Pass extra arguments to pytest
./scripts/test.sh -- -x --pdb
./scripts/test.sh -- --maxfail=3
```

### check.sh - Full Check Suite

Combines linting and testing in one command.

```bash
# Run all checks
./scripts/check.sh

# Fix lint issues first, then test
./scripts/check.sh --fix

# Only lint (no tests)
./scripts/check.sh --lint-only

# Only test (no lint)
./scripts/check.sh --test-only
```

### format.sh - Code Formatting

Auto-formats code across the project.

```bash
# Format everything
./scripts/format.sh

# Check only (CI mode, no modifications)
./scripts/format.sh --check

# Python only
./scripts/format.sh --python

# Frontend only
./scripts/format.sh --frontend

# Specific paths
./scripts/format.sh src/specinit
```

**Tools used:**
- **Python**: ruff format, ruff check --fix
- **Frontend**: Prettier, ESLint --fix

### clean.sh - Cleanup

Removes build artifacts and caches.

```bash
# Standard cleanup
./scripts/clean.sh

# Preview what would be deleted
./scripts/clean.sh --dry-run

# Clean everything (including node_modules, .venv)
./scripts/clean.sh --all

# Clean only old log files
./scripts/clean.sh --logs

# Clean logs older than 30 days
./scripts/clean.sh --logs-days 30
```

**What it cleans:**

| Category | Items |
|----------|-------|
| Python cache | `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/` |
| Tool cache | `.ruff_cache/`, `.mypy_cache/` |
| Build | `dist/`, `build/`, `*.egg-info/` |
| Coverage | `.coverage`, `htmlcov/`, `coverage.xml` |
| Logs | Old files in `.logs/` (default: 7+ days old) |
| With `--all` | `node_modules/`, `.venv/`, `frontend/dist/` |

## Logging

All scripts support logging to `.logs/` directory:

```
.logs/
├── lint/
│   ├── 2024-01-15_143022_lint.log
│   └── latest.log -> 2024-01-15_143022_lint.log
├── test/
│   ├── 2024-01-15_143045_test.log
│   └── latest.log -> 2024-01-15_143045_test.log
└── check/
    └── ...
```

- Logs are timestamped and organized by script type
- `latest.log` symlink always points to the most recent run
- Use `--no-log` to disable logging
- Use `./scripts/clean.sh --logs` to clean old logs

## Library Files

The `scripts/lib/` directory contains shared utilities:

### lib/common.sh

Shared functions used by all scripts:
- Color output (`log_info`, `log_success`, `log_error`, `log_warn`)
- Logging to file with timestamps
- Exit code constants
- Duration formatting
- Command existence checks

### lib/detect.sh

Auto-detection functions:
- Language detection (Python, TypeScript/JavaScript)
- Framework detection (React, FastAPI, Next.js, etc.)
- Tool detection (pytest, ruff, ESLint, Prettier)
- Package manager detection (npm, yarn, pnpm)
- Directory detection (source dirs, test dirs, frontend dir)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Lint failed |
| 2 | Tests failed |
| 3 | Setup failed |
| 4 | Missing dependencies |
| 5 | Invalid arguments |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NO_COLOR` | Disable colored output |
| `VERBOSE` | Enable verbose output |
| `QUIET` | Enable quiet mode |
| `LOG_DIR` | Override log directory (default: `.logs`) |
| `PYTEST_ADDOPTS` | Additional pytest options |

## Extending Scripts

### Adding a New Linter

Edit `scripts/lint.sh` and add a new function:

```bash
lint_new_tool() {
    if ! command_exists new_tool; then
        log_debug "new_tool not installed, skipping"
        return 0
    fi

    log_info "Running new_tool..."
    if new_tool check .; then
        log_success "new_tool passed"
    else
        log_error "new_tool found issues"
        ((ERRORS++))
    fi
}
```

### Adding Language Support

Edit `scripts/lib/detect.sh`:

```bash
detect_go() {
    [[ -f "go.mod" ]] || [[ -f "go.sum" ]]
}
```

Then update the relevant scripts to use the detection function.

## Integration with CI

These scripts are designed to work in CI environments:

```yaml
# GitHub Actions example
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Setup
        run: ./scripts/setup.sh --ci
      - name: Lint
        run: ./scripts/lint.sh
      - name: Test
        run: ./scripts/test.sh
```

## Troubleshooting

### "Permission denied" when running scripts

```bash
chmod +x scripts/*.sh scripts/lib/*.sh
```

### Scripts not finding Python tools

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
```

### Logs filling up disk space

```bash
# Clean logs older than 7 days
./scripts/clean.sh --logs

# Or clean all logs
rm -rf .logs/*
```

### Colors not showing

Check that your terminal supports ANSI colors. Use `--verbose` to ensure output isn't being suppressed.
