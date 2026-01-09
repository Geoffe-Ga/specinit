# Expand Python Quality Tools to World-Class Standards

## Summary
Add missing Python quality tools from MAXIMUM_QUALITY_ENGINEERING.md to achieve comprehensive code quality enforcement in the specinit repository itself.

## Context
Currently, specinit uses ruff, mypy, xenon, radon, vulture, and import-linter. The MAXIMUM_QUALITY_ENGINEERING plan recommends additional tools for world-class quality:
- `bandit` - Security linting
- `safety` - Dependency security scanning
- `interrogate` - Docstring coverage enforcement
- `pydocstyle` - Docstring style enforcement
- `darglint` - Docstring-code consistency
- `tryceratops` - Exception handling best practices
- `refurb` - Modern Python suggestions
- `pyupgrade` - Automatic syntax upgrades
- `autoflake` - Remove unused imports/variables
- `dead` - Dead code detection (alternative to vulture)
- `prospector` - Meta-linter orchestrator
- `commitizen` - Commit message validation

## Tasks
- [ ] Add missing tools to `pyproject.toml` `[project.optional-dependencies]` dev section
- [ ] Configure each tool in `pyproject.toml` with strict settings (see MAXIMUM_QUALITY_ENGINEERING Part 2.1)
- [ ] Add bandit security scanning to pre-commit hooks
- [ ] Add interrogate docstring coverage check (95% threshold)
- [ ] Add pydocstyle for Google-style docstring enforcement
- [ ] Add tryceratops for exception handling validation
- [ ] Add refurb for modern Python suggestions
- [ ] Add pyupgrade to automatically upgrade syntax to Python 3.11+
- [ ] Add autoflake to remove unused imports/variables
- [ ] Add commitizen for conventional commit enforcement
- [ ] Update `scripts/lint.sh` to run new tools
- [ ] Update `scripts/format.sh` to run auto-fixable tools
- [ ] Run all new tools and fix any issues found
- [ ] Update CLAUDE.md and AGENTS.md documentation

## Acceptance Criteria
- All tools from MAXIMUM_QUALITY_ENGINEERING Part 2.1 are installed
- `pyproject.toml` has strict configurations for each tool
- `pre-commit run --all-files` includes all new checks
- All new checks pass on current codebase
- Documentation updated with new tool usage

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 2.1
- Issue #81 (Python world-class complexity standards)

## Labels
enhancement, quality, tooling

## Dependencies
None - can be implemented independently
