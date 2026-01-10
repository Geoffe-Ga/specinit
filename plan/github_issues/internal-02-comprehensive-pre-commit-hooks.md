# Implement Comprehensive Pre-Commit Hook Suite

## Summary
Expand `.pre-commit-config.yaml` to include all security, quality, and consistency checks from MAXIMUM_QUALITY_ENGINEERING.md.

## Context
Current pre-commit hooks cover basic checks (ruff, mypy, complexity). The MAXIMUM_QUALITY_ENGINEERING plan specifies a comprehensive hook suite including:
- Git integrity checks (large files, merge conflicts, symlinks)
- File format validation (TOML, YAML, JSON)
- Security scanning (detect-secrets, bandit)
- Advanced code quality hooks
- Commit message validation (commitizen)

## Tasks
- [ ] Add pre-commit-hooks repository checks:
  - [ ] check-added-large-files (max 500KB)
  - [ ] check-case-conflict
  - [ ] check-merge-conflict
  - [ ] check-symlinks
  - [ ] check-toml, check-yaml, check-json
  - [ ] detect-private-key
  - [ ] end-of-file-fixer
  - [ ] fix-byte-order-marker
  - [ ] mixed-line-ending (enforce LF)
  - [ ] no-commit-to-branch (protect main)
  - [ ] trailing-whitespace
  - [ ] check-ast
  - [ ] debug-statements
  - [ ] check-docstring-first
- [ ] Add detect-secrets hook with baseline file
- [ ] Add bandit security hook
- [ ] Add interrogate docstring coverage hook
- [ ] Add vulture dead code detection hook
- [ ] Add pyupgrade hook (--py311-plus)
- [ ] Add autoflake hook (remove unused imports)
- [ ] Add tryceratops exception handling hook
- [ ] Add refurb modern Python hook
- [ ] Add commitizen hook for commit-msg stage
- [ ] Configure `ci.autofix_commit_msg` and `ci.autoupdate_commit_msg`
- [ ] Set `ci.skip = []` to ensure no hooks are skipped in CI
- [ ] Generate `.secrets.baseline` file
- [ ] Test all hooks pass on current codebase
- [ ] Update documentation

## Acceptance Criteria
- `.pre-commit-config.yaml` matches MAXIMUM_QUALITY_ENGINEERING Part 2.1 template
- All hooks pass on current codebase
- `pre-commit run --all-files` completes successfully
- `.secrets.baseline` exists and is tracked
- Commit message validation works (test with invalid commit)
- Documentation updated

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 2.1 lines 280-412

## Labels
enhancement, quality, ci-cd

## Dependencies
- Requires internal-01-expand-python-quality-tools (for new tool installations)
