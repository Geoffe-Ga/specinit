# CLAUDE.md - AI Context for SpecInit Development

## Critical Rules

### No Shortcuts

**Never take shortcuts when fixing tests or checks:**
- Do not comment out or skip failing tests
- Do not relax linter rules or filters to make errors go away
- Do not change test assertions to match incorrect behavior
- All tests must test real functionality
- All checks must enforce valid requirements
- If a test fails, fix the underlying code, not the test (unless the test itself is wrong)

### Working Directory

**Always operate from the project root directory. Do not `cd` into subdirectories when running commands.** All paths in commands should be relative to the project root.

### Use Scripts for Consistency

**Always use the provided scripts in `scripts/` or `pre-commit` for running tests and checks.** This ensures consistency between local development, pre-commit hooks, and CI.

```bash
# Use these commands (in order of preference)
pre-commit run --all-files     # Best: runs all checks as CI would
./scripts/lint.sh              # Run all linting (ruff check, ruff format --check, mypy)
./scripts/test.sh              # Run all tests with coverage
./scripts/check.sh             # Run both lint and test

# Do NOT run these directly (use scripts instead)
python -m ruff check src/      # Use ./scripts/lint.sh or pre-commit
python -m mypy src/            # Use ./scripts/lint.sh or pre-commit
pytest tests/                  # Use ./scripts/test.sh
```

**Why?** Running tools directly via `python -m` or bare commands bypasses the virtual environment activation and may use system Python. Scripts ensure the correct environment is used.

## Overview

SpecInit is a local-first CLI tool that transforms project ideas into working codebases using Claude AI. Users answer 5-6 questions through a web interface, and the tool orchestrates Claude API calls to generate complete projects with documentation, tests, and configuration.

## Architecture

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| CLI | `src/specinit/cli/main.py` | Click-based CLI: `init`, `new`, `list`, `config` |
| Web Server | `src/specinit/server/app.py` | FastAPI with WebSocket for real-time progress |
| Generator | `src/specinit/generator/` | 8-step generation orchestration |
| Storage | `src/specinit/storage/` | Config (YAML + keyring), History (SQLite) |
| GitHub | `src/specinit/github/` | Issue-driven development workflow |
| Frontend | `frontend/` | React + Vite + Tailwind form wizard |

### 8-Step Generation Process

1. **Product Specification** - Claude generates comprehensive spec → `plan/product-spec.md`
2. **Project Structure** - Create directories and files
3. **Documentation** - README, CONTRIBUTING, CLAUDE.md
4. **Developer Tooling** - Linters, pre-commit, CI/CD
5. **Validation** - Verify structure (local)
6. **Dependencies** - Prepare package files (local)
7. **Git Initialization** - Init repo, initial commit (local)
8. **Demo Code** - Working implementation with tests

## Key Design Decisions

1. **Local-first**: All data on user's machine, no telemetry
2. **Keyring for secrets**: API keys via OS keyring, not config files
3. **Cost transparency**: Every API call tracked and displayed
4. **TDD emphasis**: Generated projects include comprehensive tests
5. **plan/ directory**: Planning docs in generated projects

## Common Tasks

### Setup
```bash
pip install -e ".[dev]"
pre-commit install
```

### Running Tests and Linting
```bash
# Recommended: Use scripts for consistency with CI
./scripts/lint.sh      # Linting only
./scripts/test.sh      # Tests only
./scripts/check.sh     # Both lint and test

# Pre-commit (runs same checks as CI)
pre-commit run --all-files
```

## File Locations

- Config: `~/.specinit/config.yaml`
- History: `~/.specinit/history.db`
- API keys: OS keyring (service: `specinit`, `specinit-github`)

## Gotchas

1. **API key validation**: Must start with `sk-ant-`
2. **Template selection**: Scoring algorithm based on platform + tech stack match
3. **GitHub token**: Separate from Anthropic key, in keyring as `specinit-github`
4. **WebSocket**: Frontend connects to `/ws/generate` for progress updates
5. **Cost tracking**: Model pricing in `src/specinit/generator/cost.py`

## Test Coverage Targets

- Overall: 90%+
- CLI commands: 90%+
- Generator functions: 90%+
- Config/Storage: 90%+
- GitHub integration: 85%+
- Server/API: 75%+
- UI components: 50%+

## Dependencies

**Runtime**: click, fastapi, uvicorn, anthropic, jinja2, pyyaml, keyring, rich, pydantic, websockets

**Development**: pytest, pytest-asyncio, pytest-cov, ruff, mypy, pre-commit, httpx
