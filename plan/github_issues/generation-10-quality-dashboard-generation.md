# Generate Quality Metrics Dashboard Configuration

## Summary
Implement generation of SonarQube/SonarCloud configuration and quality metrics tracking for generated projects, based on MAXIMUM_QUALITY_ENGINEERING.md Part 9.

## Context
Generated projects should have automatic quality metrics tracking with dashboards, badges, and alerts for the 10 mandatory metrics from Part 9.1.

## Tasks

### SonarQube Configuration
- [ ] Create `sonar-project.properties` template (lines 1869-1888)
- [ ] Configure project metadata
- [ ] Set source and test paths
- [ ] Configure coverage exclusions
- [ ] Set quality gate requirements
- [ ] Configure language-specific settings

### Quality Thresholds Configuration
- [ ] Create `quality-gates/coverage-thresholds.json` template
- [ ] Define global thresholds:
  - [ ] Branches: 90%
  - [ ] Functions: 95%
  - [ ] Lines: 90%
  - [ ] Statements: 90%
- [ ] Define per-file thresholds:
  - [ ] Domain layer: 95% functions, 95% lines
  - [ ] Application layer: 95% functions, 90% lines
  - [ ] Infrastructure: 90% functions, 85% lines
- [ ] Set mutation score minimum: 80%

### Complexity Limits Configuration
- [ ] Create `quality-gates/complexity-limits.json`
- [ ] Python limits:
  - [ ] Cyclomatic complexity: ≤10
  - [ ] Cognitive complexity: ≤15
  - [ ] Maintainability index: ≥20
- [ ] TypeScript limits:
  - [ ] Cyclomatic complexity: ≤10
  - [ ] Cognitive complexity: ≤15
  - [ ] Max file length: 300 lines
  - [ ] Max function length: 50 lines

### Architecture Rules Documentation
- [ ] Create `quality-gates/architecture-rules.json`
- [ ] Document import-linter contracts
- [ ] Document dependency-cruiser rules
- [ ] Define layer boundaries
- [ ] List forbidden dependencies

### CI Integration
- [ ] Add SonarCloud to CI workflow
- [ ] Upload coverage reports
- [ ] Upload test results
- [ ] Configure quality gate check
- [ ] Add PR decoration with metrics

### Badge Generation
- [ ] Add coverage badge to README
- [ ] Add quality gate badge
- [ ] Add security rating badge
- [ ] Add build status badge
- [ ] Add mutation score badge (if available)

### Quality Dashboard Documentation
- [ ] Create `docs/quality-metrics.md` with:
  - [ ] Metric definitions
  - [ ] Current thresholds
  - [ ] How to interpret metrics
  - [ ] How to improve scores
  - [ ] Dashboard access instructions

### Metric Collection Scripts
- [ ] Create `scripts/collect-metrics.sh` to:
  - [ ] Run coverage analysis
  - [ ] Calculate complexity metrics
  - [ ] Check mutation score
  - [ ] Verify documentation coverage
  - [ ] Check dependency freshness
  - [ ] Scan for vulnerabilities
  - [ ] Generate report

### Alerts and Notifications
- [ ] Configure quality gate failure alerts
- [ ] Set up PR comment automation with metrics
- [ ] Add threshold violation notifications
- [ ] Create quality trend reports

### Metrics Tracked
- [ ] Code Coverage (pytest-cov/jest) → ≥90%
- [ ] Branch Coverage → ≥85%
- [ ] Mutation Score (mutmut/Stryker) → ≥80%
- [ ] Cyclomatic Complexity (xenon/eslint) → ≤10
- [ ] Cognitive Complexity (radon/sonarjs) → ≤15
- [ ] Maintainability Index (radon) → ≥20
- [ ] Technical Debt Ratio (SonarCloud) → ≤5%
- [ ] Documentation Coverage (interrogate) → ≥95%
- [ ] Dependency Freshness → ≤30 days
- [ ] Security Vulnerabilities → 0 critical/high

### Generator Integration
- [ ] Generate quality-gates/ directory during Step 4
- [ ] Create sonar-project.properties
- [ ] Generate threshold configurations
- [ ] Add quality metrics collection script
- [ ] Update CI to report metrics
- [ ] Add badges to README
- [ ] Create quality metrics documentation

### SonarCloud Setup Instructions
- [ ] Add SonarCloud setup guide to README
- [ ] Document token configuration
- [ ] Explain quality gate customization
- [ ] Add troubleshooting section

### Local Quality Dashboard (Optional)
- [ ] Consider generating local dashboard HTML
- [ ] Display metrics summary
- [ ] Show trends over time
- [ ] Include visualization

### Validation
- [ ] Verify sonar-project.properties valid
- [ ] Test metric collection script
- [ ] Check CI integration working
- [ ] Validate badges render
- [ ] Ensure thresholds enforced

## Acceptance Criteria
- sonar-project.properties generated
- quality-gates/ directory with threshold configs
- All 10 mandatory metrics tracked
- CI uploads metrics to SonarCloud
- Quality gate blocks PRs on violations
- README includes metric badges
- Documentation explains metrics
- Metric collection script works
- PR comments show quality metrics
- Thresholds match MAXIMUM_QUALITY_ENGINEERING

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 9
- Issue internal-06 (Quality metrics for specinit itself)

## Labels
enhancement, generation, quality, monitoring

## Dependencies
- Coordinated with generation-05 (CI/CD pipeline templates)
