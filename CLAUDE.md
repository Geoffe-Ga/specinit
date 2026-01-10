# CLAUDE.md - Claude AI Development Context for SpecInit

> This file provides context specifically for Claude (Anthropic's AI) when working on this codebase. For provider-agnostic instructions, see `AGENTS.md`.

## Critical Rules

These are NON-NEGOTIABLE. Claude must follow these rules without exception.

### Rule 1: No Shortcuts

**Never take shortcuts when fixing tests or checks:**

```
FORBIDDEN actions:
✗ Comment out or skip failing tests
✗ Add # noqa or # type: ignore to suppress errors
✗ Relax linter rules or filters to make errors disappear
✗ Change test assertions to match incorrect behavior
✗ Disable pre-commit hooks or CI checks
✗ Catch and silence exceptions without handling them

REQUIRED actions:
✓ Fix the root cause of every failure
✓ Add tests for all new functionality
✓ Run the full test suite before suggesting changes are complete
✓ Preserve existing test coverage levels
```

### Rule 2: Use Project Scripts

**Always use provided scripts for running tests and checks.** This ensures consistency between local development, pre-commit hooks, and CI.

```bash
# CORRECT - Use these commands (in order of preference)
pre-commit run --all-files     # Best: runs all checks as CI would
./scripts/lint.sh              # Linting: ruff check, ruff format, mypy
./scripts/complexity.sh        # Complexity: xenon, radon, import-linter
./scripts/test.sh              # Tests: pytest with coverage
./scripts/check.sh             # Both lint and test

# FORBIDDEN - Never run tools directly
python -m ruff check src/      # May use wrong Python
python -m mypy src/            # May use wrong Python
pytest tests/                  # Bypasses coverage and config
ruff format src/               # May use wrong version
xenon src/                     # May use wrong Python or thresholds
```

**Why?** Running tools directly via `python -m` or bare commands may use system Python instead of the virtual environment. Scripts ensure:
- Correct Python interpreter
- Correct tool versions
- Consistent configuration
- Same behavior as CI

### Rule 3: Work From Project Root

**Always operate from the project root directory.** Never `cd` into subdirectories when running commands. All paths in commands should be relative to the project root.

```bash
# CORRECT
pytest tests/unit/test_cli.py
./scripts/lint.sh

# FORBIDDEN
cd tests && pytest unit/test_cli.py
cd src && python -m specinit
```

### Rule 4: Verify Before Declaring Done

Before stating that a task is complete, Claude must:

1. Run `pre-commit run --all-files` and confirm all checks pass
2. Run `./scripts/test.sh` and confirm all tests pass
3. Check that no new warnings or deprecations were introduced
4. Verify the change actually solves the original problem

### Rule 5: Efficient CI Monitoring

**Do not use blocking `--watch` commands for CI checks.** These waste resources and context.

```bash
# FORBIDDEN - Blocks indefinitely, wastes context
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

## Project Overview

SpecInit is a local-first CLI tool that transforms project ideas into working codebases using Claude AI. Users answer 5-6 questions through a web interface, and the tool orchestrates Claude API calls to generate complete projects with documentation, tests, and configuration.

### Key Principles

1. **Local-first**: All data stored on user's machine, no telemetry
2. **Cost transparency**: Every API call tracked and displayed to user
3. **Security-conscious**: API keys in OS keyring, never in files
4. **TDD emphasis**: Generated projects include comprehensive tests
5. **Quality gates**: Pre-commit hooks enforce standards

## Architecture

### Component Map

| Component | Location | Purpose | Key Files |
|-----------|----------|---------|-----------|
| CLI | `src/specinit/cli/` | User commands | `main.py` |
| Server | `src/specinit/server/` | Web UI backend | `app.py` |
| Generator | `src/specinit/generator/` | Project creation | `orchestrator.py`, `prompts.py` |
| Storage | `src/specinit/storage/` | Persistence | `config.py`, `history.py` |
| GitHub | `src/specinit/github/` | GitHub integration | `service.py`, `workflow.py` |
| Frontend | `frontend/` | React form wizard | `src/App.tsx` |

### Data Flow

```
User Input (Web UI)
       ↓
    FastAPI Server (WebSocket)
       ↓
    Generator Orchestrator
       ↓
    Claude API (via Anthropic SDK)
       ↓
    File Writer → Generated Project
       ↓
    History Manager (SQLite)
```

### 8-Step Generation Process

1. **Product Specification** - Claude generates comprehensive spec → `plan/product-spec.md`
2. **Project Structure** - Create directories and files
3. **Documentation** - README, CONTRIBUTING, CLAUDE.md
4. **Developer Tooling** - Linters, pre-commit, CI/CD
5. **Validation** - Verify structure (local, no API)
6. **Dependencies** - Prepare package files (local)
7. **Git Initialization** - Init repo, initial commit (local)
8. **Demo Code** - Working implementation with tests

## Common Tasks

### Initial Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Full test suite with coverage (RECOMMENDED)
./scripts/test.sh

# Single test file
source .venv/bin/activate && pytest tests/unit/test_cli.py -v

# Single test
source .venv/bin/activate && pytest tests/unit/test_cli.py::TestInitCommand::test_init_with_valid_api_key -v

# With print output visible
source .venv/bin/activate && pytest tests/unit/test_cli.py -v -s
```

### Running Linting

```bash
# All linting checks (RECOMMENDED)
./scripts/lint.sh

# Or via pre-commit
pre-commit run --all-files

# Auto-fix issues (RECOMMENDED)
./scripts/format.sh
```

### Running Complexity Checks

```bash
# Check code complexity and architectural boundaries (RECOMMENDED)
./scripts/complexity.sh

# Check Python only
./scripts/complexity.sh --python

# Check frontend only
./scripts/complexity.sh --frontend

# Via pre-commit
pre-commit run complexity --all-files
```

**What does this check?**
- **Cyclomatic Complexity** (xenon): Ensures functions aren't too complex
- **Cognitive Complexity** (radon cc): Measures mental effort to understand code
- **Dead Code Detection** (vulture): Finds unused code
- **Maintainability Index** (radon mi): Measures code maintainability
- **Architectural Boundaries** (import-linter): Prevents layer violations
- **Module Dependencies** (dependency-cruiser): Prevents circular dependencies (frontend)

**Current Thresholds (World-Class Standards - Issues #81, #82):**

**Python:**
- **Cyclomatic** (xenon):
  - Absolute: C (11-20) - Allows workflow orchestration methods
  - Modules: B (6-10) - Tightened from C
  - Average: A (1-5) - Tightened from B
- **Cognitive** (radon cc):
  - Rejects: D+ (>20) - Too complex, must refactor
  - Allows: A/B/C (1-20) - Acceptable, with C for workflow methods only
  - Rationale: Workflow orchestration (iterate_ci, handle_reviews) inherently reaches C-rank
- **Dead Code** (vulture): 0% tolerance (comprehensive whitelist for false positives)
- **Architectural contracts**: 6 enforced, see `.importlinter`

**TypeScript/Frontend:**
- **Cyclomatic** (ESLint complexity): ≤10 (tightened from 15)
- **Max nesting** (max-depth): ≤3 (tightened from 4)
- **Max lines/file** (max-lines): ≤200 (tightened from 300)
- **Max lines/function** (max-lines-per-function): ≤75 (tightened from 150)
- **Max parameters** (max-params): ≤4 (tightened from 5)
- **Max statements** (max-statements): ≤15 (tightened from 20)
- **Cognitive** (sonarjs/cognitive-complexity): ≤10
- **Duplicate strings** (sonarjs/no-duplicate-string): threshold 3
- **Code duplication** (jscpd): <3% (currently 0.37%)
- **Dead code** (knip): 0% unused exports/imports

**If complexity checks fail:**
1. Read the error message - it shows which function/module/component is too complex
2. **Python**: Extract helper functions, reduce nesting, simplify conditionals
3. **TypeScript/React**: Extract custom hooks, split into sub-components, use composition patterns
4. For Python workflow methods at C-rank: acceptable if justified by orchestration needs
5. See #70 (D→C refactoring), #81 (Python world-class), #82 (TypeScript world-class) for guidance
6. DO NOT suppress warnings - fix the root cause (Rule 1: No Shortcuts)

### Adding a New Feature

1. Create tests first in `tests/unit/test_<module>.py`
2. Implement the feature
3. Run `./scripts/test.sh` to verify tests pass
4. Run `pre-commit run --all-files` to verify linting
5. Commit with conventional commit message

### Debugging Test Failures

```bash
# Run with verbose output
source .venv/bin/activate && pytest tests/unit/test_cli.py -v --tb=long

# Stop on first failure
source .venv/bin/activate && pytest tests/unit/test_cli.py -x

# Run specific test matching pattern
source .venv/bin/activate && pytest tests/ -k "test_init"

# Show local variables in traceback
source .venv/bin/activate && pytest tests/unit/test_cli.py -v --tb=short -l
```

## File Locations

### User Data (Runtime)

| Data | Location | Format |
|------|----------|--------|
| Configuration | `~/.specinit/config.yaml` | YAML |
| Project history | `~/.specinit/history.db` | SQLite |
| Anthropic API key | OS keyring (`specinit`) | Encrypted |
| GitHub token | OS keyring (`specinit-github`) | Encrypted |

### Source Code

| Purpose | Location |
|---------|----------|
| Python package | `src/specinit/` |
| CLI entry point | `src/specinit/cli/main.py` |
| API server | `src/specinit/server/app.py` |
| Generation logic | `src/specinit/generator/orchestrator.py` |
| Prompt templates | `src/specinit/generator/prompts.py` |
| Project templates | `templates/` |
| Tests | `tests/unit/` |
| Test fixtures | `tests/conftest.py` |

## Testing Conventions

### Test Organization

```python
class TestFeatureName:
    """Tests for [feature/component being tested]."""

    @pytest.fixture
    def setup_specific_state(self):
        """Set up state needed for these tests."""
        ...

    def test_success_case(self):
        """Should [expected behavior] when [condition]."""
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_edge_case(self):
        """Should handle [edge case description]."""
        ...

    def test_error_case(self):
        """Should raise [Error] when [invalid condition]."""
        with pytest.raises(ExpectedError):
            ...
```

### Common Fixtures

From `conftest.py`:
- `temp_dir` - Temporary directory, cleaned up after test
- `mock_home` - Mocked home directory for config isolation
- `_mock_home` - Same as mock_home (underscore = unused in test)

### Mocking Patterns

```python
# Mock a class
with patch("specinit.cli.main.ConfigManager") as mock:
    mock_instance = MagicMock()
    mock_instance.get_api_key.return_value = "sk-ant-test"
    mock.return_value = mock_instance
    ...

# Mock a function
with patch("specinit.server.app.start_server") as mock_server:
    mock_server.return_value = None
    ...
```

## Gotchas and Non-Obvious Behaviors

1. **API Key Format**: Must start with `sk-ant-` - validation in `cli/main.py`

2. **Template Selection**: Uses scoring algorithm in `generator/templates.py` based on platform + tech stack match scores

3. **GitHub Token**: Stored separately from Anthropic key, service name is `specinit-github` not `specinit`

4. **WebSocket Path**: Frontend connects to `/ws/generate` for real-time progress updates

5. **Cost Tracking**: Model pricing constants in `generator/cost.py` - must be updated when Anthropic changes prices

6. **History Database**: Created lazily on first use, uses SQLite with path `~/.specinit/history.db`

7. **Config Patching in Tests**: Must patch `HISTORY_DIR` and `HISTORY_DB` constants, not just the module

8. **Fixture Naming**: Unused fixtures must start with underscore (`_mock_home`) to pass linting

9. **Import at Module Level**: Ruff requires imports at top of file, not inside functions - use fixtures for deferred imports

## Security Considerations

### API Keys

```python
# CORRECT - Use keyring
import keyring
api_key = keyring.get_password("specinit", "api_key")

# FORBIDDEN - Never store in files or env vars
api_key = os.environ["ANTHROPIC_API_KEY"]  # Bad
api_key = config["api_key"]  # Bad if config is a file
```

### Path Handling

```python
# CORRECT - Validate paths
from pathlib import Path

def safe_path(base: Path, user_input: str) -> Path:
    """Create a safe path within base directory."""
    # Sanitize input
    clean_name = re.sub(r'[^\w\-.]', '', user_input)
    target = base / clean_name

    # Verify it's within base (prevents path traversal)
    if not target.resolve().is_relative_to(base.resolve()):
        raise ValueError("Invalid path")
    return target

# FORBIDDEN - Direct path concatenation with user input
project_path = base_dir / user_input  # Path traversal vulnerability!
```

### Subprocess Safety

```python
# CORRECT - Use list form, no shell
subprocess.run(["git", "init"], cwd=project_path, check=True)

# FORBIDDEN - Shell injection vulnerability
subprocess.run(f"git init {project_path}", shell=True)  # Bad!
```

## Test Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Overall | 90%+ | 91% |
| CLI | 90%+ | 97% |
| Generator | 90%+ | 95%+ |
| Storage | 90%+ | 100% |
| GitHub | 85%+ | 85%+ |
| Server | 75%+ | 78% |

## Dependencies

### Runtime

```
click          - CLI framework
fastapi        - Web framework
uvicorn        - ASGI server
anthropic      - Claude API client
jinja2         - Template engine
pyyaml         - Config file parsing
keyring        - Secure credential storage
rich           - Terminal formatting
pydantic       - Data validation
websockets     - Real-time communication
```

### Development

```
pytest         - Test framework
pytest-asyncio - Async test support
pytest-cov     - Coverage reporting
ruff           - Linter and formatter
mypy           - Type checker
pre-commit     - Git hooks
httpx          - HTTP client for testing

# Advanced testing infrastructure (Issue #88)
hypothesis         - Property-based testing
mutmut             - Mutation testing
pytest-benchmark   - Performance benchmarking
pytest-snapshot    - Snapshot testing
pytest-timeout     - Prevent hanging tests
pytest-randomly    - Detect test interdependencies (disabled by default)
pytest-xdist       - Parallel test execution

# Python complexity tools
xenon          - Cyclomatic complexity checker
radon          - Cognitive complexity and maintainability metrics
vulture        - Dead code detection
import-linter  - Architectural boundary enforcement

# Python world-class quality tools (Issue #86)
bandit         - Security linting
safety         - Dependency security scanning
interrogate    - Docstring coverage enforcement
pydocstyle     - Docstring style enforcement (Google convention)
darglint       - Docstring-code consistency checking
tryceratops    - Exception handling best practices
refurb         - Modern Python suggestions
pyupgrade      - Automatic syntax upgrades to Python 3.11+
autoflake      - Remove unused imports/variables
dead           - Dead code detection (alternative to vulture)
commitizen     - Conventional commit validation

# TypeScript/Frontend complexity tools
eslint-plugin-sonarjs  - Cognitive complexity and code smells
jscpd                  - Code duplication detection
knip                   - Dead code and unused exports detection
dependency-cruiser     - Module dependency analysis
```

## Git Workflow

### Commit Message Format

```
type: short description (imperative mood)

Optional longer explanation of what and why.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <model>@anthropic.com
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `style`, `perf`

### Before Committing

1. `pre-commit run --all-files` - All hooks must pass
2. `./scripts/test.sh` - All tests must pass
3. Review diff for accidental changes
4. Write descriptive commit message

## Claude-Specific Instructions

### Context Management

When working on this project, Claude should:

1. **Read relevant files first** before making changes
2. **Use the Todo tool** to track multi-step tasks
3. **Verify changes** by running tests after edits
4. **Explain reasoning** when making non-obvious decisions

### Tool Usage Preferences

```
Prefer:                      Over:
─────────────────────────────────────
Read tool                    Bash cat/head/tail
Edit tool                    Bash sed/awk
Grep tool                    Bash grep/rg
Glob tool                    Bash find/ls
```

### When to Ask for Clarification

- Ambiguous requirements that could be interpreted multiple ways
- Changes that would significantly alter architecture
- Security-sensitive modifications
- Breaking changes to public APIs

### Response Style

- Be concise but complete
- Show exact commands to run
- Include file paths in code references (e.g., `src/specinit/cli/main.py:45`)
- Proactively mention potential issues or alternatives
