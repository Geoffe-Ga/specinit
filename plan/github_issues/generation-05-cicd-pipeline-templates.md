# Generate Comprehensive CI/CD Pipeline Templates

## Summary
Implement generation of GitHub Actions workflows with all 7 job categories from MAXIMUM_QUALITY_ENGINEERING.md Part 3.

## Context
Generated projects should have complete CI/CD pipelines including code quality, tests, mutation testing, security scanning, dependency review, architecture validation, and documentation checks.

## Tasks

### CI Workflow Template (Python)
- [ ] Create `.github/workflows/ci.yml` template based on Part 3.1 (lines 902-1155)
- [ ] Job 1: Code Quality
  - [ ] Ruff linting and formatting
  - [ ] Black and isort checks
  - [ ] MyPy type checking
  - [ ] Pylint score ≥9.0
  - [ ] Bandit security scan
  - [ ] Safety dependency check
  - [ ] Vulture dead code detection
  - [ ] Radon complexity metrics
  - [ ] Xenon complexity gates
  - [ ] Interrogate docstring coverage
- [ ] Job 2: Tests
  - [ ] Unit tests with coverage (≥90%)
  - [ ] Integration tests
  - [ ] Property-based tests
  - [ ] Matrix testing (Python 3.11, 3.12)
  - [ ] Coverage upload to Codecov
  - [ ] Test result artifacts
- [ ] Job 3: Mutation Testing
  - [ ] Run mutmut
  - [ ] Check mutation score ≥80%
  - [ ] Upload mutation results
- [ ] Job 4: Security Scanning
  - [ ] Trivy vulnerability scanner
  - [ ] Semgrep static analysis
  - [ ] SARIF upload to Code Scanning
  - [ ] Multi-ruleset scanning (python, security-audit, secrets, owasp-top-ten)
- [ ] Job 5: Dependency Review
  - [ ] Dependency review action (PRs only)
  - [ ] Fail on moderate+ severity
  - [ ] License blocking (GPL-3.0, AGPL-3.0)
- [ ] Job 6: Architecture Validation
  - [ ] import-linter contract checks
  - [ ] pydeps circular dependency detection
- [ ] Job 7: Documentation
  - [ ] README validation
  - [ ] CHANGELOG presence check
  - [ ] API doc generation (pdoc)
  - [ ] Docstring coverage verification

### CI Workflow Template (TypeScript)
- [ ] Create `.github/workflows/ci.yml` template based on Part 3.2 (lines 1159-1270)
- [ ] Job 1: Code Quality
  - [ ] Prettier format check
  - [ ] ESLint with --max-warnings 0
  - [ ] TypeScript type checking (tsc --noEmit)
  - [ ] depcheck for unused dependencies
  - [ ] knip for unused exports
  - [ ] madge for circular dependencies
  - [ ] publint for package validation
- [ ] Job 2: Tests
  - [ ] Jest/Vitest unit tests
  - [ ] Coverage threshold enforcement (90%)
  - [ ] Integration tests
  - [ ] E2E tests (Playwright)
- [ ] Job 3: Mutation Testing
  - [ ] Stryker mutation testing
  - [ ] Dashboard upload
- [ ] Job 4: Security
  - [ ] npm audit (moderate level)
  - [ ] Snyk security scan

### CD Workflow Template
- [ ] Create `.github/workflows/cd.yml` for deployments
- [ ] Triggered on tags or main branch
- [ ] Build artifacts
- [ ] Run smoke tests
- [ ] Deploy to environment (placeholder for user to configure)
- [ ] Rollback capability

### Security Workflow Template
- [ ] Create `.github/workflows/security.yml`
- [ ] Scheduled daily security scans
- [ ] CodeQL analysis
- [ ] SAST scanning
- [ ] Dependency updates check

### Dependency Review Workflow
- [ ] Create `.github/workflows/dependency-review.yml`
- [ ] Automated dependency review on PRs
- [ ] Vulnerability scanning
- [ ] License compliance

### Workflow Configuration
- [ ] Add concurrency control to cancel outdated runs
- [ ] Configure job dependencies
- [ ] Add environment variables for thresholds
- [ ] Configure artifact retention
- [ ] Add status badge configurations

### Generator Integration
- [ ] Generate workflows during Step 4 (Developer Tooling)
- [ ] Detect project language and use appropriate template
- [ ] Customize workflow based on project type (CLI, API, library)
- [ ] Ensure workflow files are valid YAML
- [ ] Add workflow dispatch triggers for manual runs

### Documentation
- [ ] Add CI/CD section to generated README
- [ ] Document workflow triggers and jobs
- [ ] Add badge examples for workflows
- [ ] Create CONTRIBUTING.md section on CI/CD
- [ ] Document how to customize workflows

### Validation
- [ ] Verify workflow YAML syntax
- [ ] Check all actions use latest versions
- [ ] Ensure required secrets documented
- [ ] Validate job dependencies logical
- [ ] Test workflows in generated projects

## Acceptance Criteria
- Python projects get comprehensive Python CI workflow
- TypeScript projects get comprehensive TypeScript CI workflow
- All 7 job categories present in CI
- CD workflow template included
- Security workflow scheduled daily
- Workflows validated and working
- Concurrency control configured
- Documentation complete
- Status badges in README

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 3
- .github/workflows/ci.yml (specinit's own workflow for reference)

## Labels
enhancement, generation, ci-cd

## Dependencies
- Should be coordinated with generation-01 (Python templates) and generation-02 (TypeScript templates)
