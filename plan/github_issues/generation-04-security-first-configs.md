# Generate Security-First Project Configurations

## Summary
Implement generation of security-focused configurations including secret detection, security scanning, dependency auditing, and secure coding practices from MAXIMUM_QUALITY_ENGINEERING.md.

## Context
Generated projects should be secure by default with automated security scanning, secret detection, dependency vulnerability checks, and security-focused linting rules.

## Tasks

### Secret Detection
- [ ] Add `detect-secrets` configuration to all projects
- [ ] Generate `.secrets.baseline` file during project creation
- [ ] Add pre-commit hook for secret detection
- [ ] Configure exclusions (test files with fake credentials)
- [ ] Add documentation on managing secrets with keyring/env vars

### Security Linting (Python)
- [ ] Add Bandit security linter configuration
- [ ] Enable all Bandit checks (no skips)
- [ ] Add Bandit to pre-commit hooks
- [ ] Configure in `pyproject.toml` with strict settings
- [ ] Add safety for dependency vulnerability scanning

### Security Linting (TypeScript)
- [ ] Add eslint-plugin-security to ESLint config
- [ ] Add eslint-plugin-no-secrets
- [ ] Enable all security rules (Part 2.2 lines 598-609):
  - [ ] detect-object-injection
  - [ ] detect-non-literal-regexp
  - [ ] detect-unsafe-regex
  - [ ] detect-child-process
  - [ ] detect-eval-with-expression
  - [ ] detect-possible-timing-attacks

### Input Validation Templates
- [ ] Generate validation schemas (Pydantic for Python, Zod for TypeScript)
- [ ] Add input sanitization examples
- [ ] Include path traversal prevention patterns
- [ ] Add SQL injection prevention (parameterized queries)
- [ ] Include XSS prevention patterns

### Dependency Security
- [ ] Configure automated dependency audits
- [ ] Add `safety check` for Python (CI daily scan)
- [ ] Add `npm audit` for Node.js
- [ ] Pin dependency versions for reproducibility
- [ ] Configure dependency license checking
- [ ] Block GPL-3.0, AGPL-3.0 licenses by default

### Security Policy Template
- [ ] Generate SECURITY.md with:
  - [ ] Vulnerability reporting process
  - [ ] Security update policy
  - [ ] Supported versions
  - [ ] Security best practices for contributors
- [ ] Add responsible disclosure guidelines

### Secure Defaults
- [ ] Generate secure configuration examples:
  - [ ] HTTPS-only (no HTTP)
  - [ ] Secure headers (CSP, HSTS, X-Frame-Options)
  - [ ] CORS configuration
  - [ ] Rate limiting
  - [ ] Input size limits
- [ ] Add authentication/authorization templates
- [ ] Include password hashing (bcrypt/argon2)
- [ ] Add session management best practices

### Code Examples
- [ ] Generate secure subprocess execution patterns (no shell=True)
- [ ] Add secure file handling (path validation)
- [ ] Include secure database query patterns
- [ ] Add secure API client examples (certificate validation)

### Generator Integration
- [ ] Add security configuration step in orchestrator
- [ ] Generate security configs during Step 4 (Developer Tooling)
- [ ] Run initial security scan and report findings
- [ ] Update prompts to emphasize security requirements
- [ ] Ensure demo code follows security best practices

### Documentation
- [ ] Add security section to generated README
- [ ] Create SECURITY.md (as above)
- [ ] Add security guidelines to CONTRIBUTING.md
- [ ] Document common vulnerabilities and prevention
- [ ] Add OWASP Top 10 checklist

## Acceptance Criteria
- Secret detection active and configured
- Security linters configured for all languages
- Dependency security scanning in place
- SECURITY.md generated
- Input validation patterns included
- Secure configuration examples present
- No hardcoded secrets in generated code
- Security scan passes on generated projects
- Documentation covers security best practices

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 2 (security tools), Part 3 (security CI), Part 8.3 (security auditor agent)
- OWASP Top 10
- CWE Top 25

## Labels
enhancement, generation, security

## Dependencies
None - can be implemented independently
