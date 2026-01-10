# Expand CI/CD Pipeline with Security and Quality Gates

## Summary
Enhance `.github/workflows/ci.yml` to include security scanning, mutation testing, architecture validation, and dependency review as specified in MAXIMUM_QUALITY_ENGINEERING.md.

## Context
Current CI runs linting and tests. MAXIMUM_QUALITY_ENGINEERING Part 3.1 specifies 7 CI job categories:
1. ✅ Code Quality (existing - linting, formatting, type checking)
2. ✅ Tests (existing - unit and integration tests)
3. ❌ Mutation Testing (missing)
4. ❌ Security Scanning (missing)
5. ❌ Dependency Review (missing)
6. ❌ Architecture Validation (missing)
7. ❌ Documentation (missing)

## Tasks

### Job 3: Mutation Testing
- [ ] Create mutation testing job (runs after tests pass)
- [ ] Install mutmut
- [ ] Run mutation tests on `src/` directory
- [ ] Check mutation score threshold (80%)
- [ ] Upload mutation results as artifact
- [ ] Add job to required checks (or make advisory initially)

### Job 4: Security Scanning
- [ ] Add security job with `security-events: write` permission
- [ ] Integrate Trivy vulnerability scanner
  - [ ] Scan filesystem for vulnerabilities
  - [ ] Output SARIF format
  - [ ] Upload to GitHub Code Scanning
- [ ] Integrate Semgrep static analysis
  - [ ] Use rulesets: p/python, p/security-audit, p/secrets, p/owasp-top-ten
  - [ ] Fail on high-severity findings
- [ ] Run bandit security linting
- [ ] Run safety dependency security check
- [ ] Fail CI on critical/high vulnerabilities

### Job 5: Dependency Review
- [ ] Add dependency-review job (pull requests only)
- [ ] Use `actions/dependency-review-action@v3`
- [ ] Fail on severity: moderate or higher
- [ ] Block GPL-3.0 and AGPL-3.0 licenses
- [ ] Add daily scheduled run for dependency audits

### Job 6: Architecture Validation
- [ ] Add architecture validation job
- [ ] Run import-linter to check architectural contracts
- [ ] Install pydeps for circular dependency detection
- [ ] Run `pydeps src/ --no-output --only-cycles`
- [ ] Fail on any violations

### Job 7: Documentation
- [ ] Add documentation job
- [ ] Check README.md exists and is valid
- [ ] Lint README with markdown-lint
- [ ] Check CHANGELOG.md exists
- [ ] Generate API docs with pdoc
- [ ] Verify docstring coverage ≥95%
- [ ] Build and validate documentation

### CI Enhancements
- [ ] Add concurrency control to cancel outdated runs
- [ ] Add job dependencies (quality → test → mutation)
- [ ] Add test result upload as artifacts
- [ ] Add coverage upload to Codecov
- [ ] Add matrix testing for Python 3.11, 3.12
- [ ] Add scheduled daily security scan (cron)
- [ ] Configure environment variables for thresholds

### Frontend CI (if not covered by #67)
- [ ] Add TypeScript type checking to CI
- [ ] Add ESLint with --max-warnings 0
- [ ] Add Prettier format check
- [ ] Add frontend test execution
- [ ] Add frontend build verification

## Acceptance Criteria
- All 7 job categories present in CI workflow
- Security scanning uploads to GitHub Code Scanning
- Mutation testing runs and enforces 80% threshold
- Architecture rules validated automatically
- Dependency review blocks risky changes
- Documentation builds and validates
- CI workflow matches MAXIMUM_QUALITY_ENGINEERING template structure
- All jobs properly depend on each other
- Failed checks block merge

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 3.1
- .github/workflows/ci.yml (current)

## Labels
enhancement, ci-cd, security

## Dependencies
- Requires internal-01 (for new tools)
- Requires internal-03 (for mutation testing)
- Requires internal-04 (for documentation validation)
