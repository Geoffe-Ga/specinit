# Generate Python Projects with World-Class Quality Configuration

## Summary
Implement Python project template generation that includes all quality tools, configurations, and standards from MAXIMUM_QUALITY_ENGINEERING.md Part 2.1.

## Context
When specinit generates a Python project, it should automatically include a comprehensive quality stack matching MAXIMUM_QUALITY_ENGINEERING standards. This ensures all generated projects start with maximum rigor.

## Tasks

### Template Creation
- [ ] Create `templates/python-quality/` directory structure
- [ ] Add complete `pyproject.toml` template with:
  - [ ] Ruff configuration (select = ["ALL"], strict settings)
  - [ ] MyPy strict configuration
  - [ ] Black formatting configuration
  - [ ] isort configuration
  - [ ] Pytest configuration with coverage ≥90%
  - [ ] Bandit security configuration
  - [ ] Interrogate docstring coverage ≥95%
  - [ ] Pydocstyle Google convention
  - [ ] Vulture dead code detection
  - [ ] Xenon complexity limits (max_absolute="B", max_modules="A", max_average="A")
  - [ ] Commitizen conventional commits
  - [ ] All tool configs from MAXIMUM_QUALITY_ENGINEERING lines 136-278

### Pre-commit Configuration Template
- [ ] Create comprehensive `.pre-commit-config.yaml` template
- [ ] Include all hooks from MAXIMUM_QUALITY_ENGINEERING lines 280-412:
  - [ ] Git integrity checks
  - [ ] Security scanning (bandit, detect-secrets)
  - [ ] Code formatting (black, isort, ruff)
  - [ ] Type checking (mypy)
  - [ ] Quality checks (interrogate, vulture, pyupgrade, autoflake, etc.)
  - [ ] Commit message validation (commitizen)

### Requirements Template
- [ ] Create `requirements-dev.txt` template with all quality tools
- [ ] Pin versions for reproducibility
- [ ] Organize by category (linting, testing, security, etc.)

### Scripts Template
- [ ] Create `scripts/lint.sh` template
- [ ] Create `scripts/format.sh` template
- [ ] Create `scripts/test.sh` template
- [ ] Create `scripts/complexity.sh` template
- [ ] Create `scripts/check.sh` template (runs all checks)
- [ ] Ensure scripts use virtual environment Python

### Test Infrastructure Template
- [ ] Create `tests/` directory structure (unit, integration, property, etc.)
- [ ] Add `conftest.py` with Hypothesis profiles and external call guards
- [ ] Add example unit test demonstrating best practices
- [ ] Add property-based test example
- [ ] Add test naming convention enforcement

### Generator Integration
- [ ] Update `generator/orchestrator.py` to use Python quality templates
- [ ] Add step to copy quality configurations
- [ ] Add step to generate `.secrets.baseline` file
- [ ] Update prompts to instruct Claude about quality requirements
- [ ] Ensure generated code follows all quality standards

### Validation
- [ ] Add validation step to verify all quality tools installed
- [ ] Run `pre-commit install` during project setup
- [ ] Run initial quality check and report results
- [ ] Provide user with quality dashboard summary

### Documentation
- [ ] Add quality standards to generated README.md
- [ ] Add CONTRIBUTING.md section on quality requirements
- [ ] Generate CLAUDE.md with quality tool usage instructions
- [ ] Document all quality thresholds and their rationale

## Acceptance Criteria
- Python projects generated with all quality tools configured
- `pyproject.toml` matches MAXIMUM_QUALITY_ENGINEERING Part 2.1
- `.pre-commit-config.yaml` includes all mandatory hooks
- Scripts for lint, format, test, complexity checks included
- Test infrastructure with 9 test categories skeleton
- Generated projects pass all quality checks immediately
- Documentation explains quality standards to users
- Validation step confirms quality setup successful

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 2.1, Part 5, Part 7
- templates/ directory (existing templates)

## Labels
enhancement, generation, quality, python

## Dependencies
None - can be implemented independently
