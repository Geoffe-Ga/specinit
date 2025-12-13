# CLAUDE.md - AI Context for SpecInit Development

## Important: Working Directory

**Always operate from the project root directory. Do not `cd` into subdirectories when running commands.** All paths in commands should be relative to the project root.

Examples:
```bash
# Correct - run from project root
pytest tests/
ruff check src/
pip install -e .

# Incorrect - do not cd into directories
cd tests && pytest  # Don't do this
cd src && ruff check .  # Don't do this
```

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

### Running Tests
```bash
pytest tests/ -v
pytest tests/unit/ -v --cov=src/specinit
```

### Linting
```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/
```

### Pre-commit
```bash
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

- CLI commands: 80%+
- Generator functions: 90%+
- Config management: 90%+
- UI components: 50%+

## Dependencies

**Runtime**: click, fastapi, uvicorn, anthropic, jinja2, pyyaml, keyring, rich, pydantic, websockets

**Development**: pytest, pytest-asyncio, pytest-cov, ruff, mypy, pre-commit, httpx
