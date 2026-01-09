# Generate Comprehensive Test Infrastructure for All Projects

## Summary
Implement automated generation of test infrastructure covering all 9 test categories from MAXIMUM_QUALITY_ENGINEERING.md Part 5.

## Context
MAXIMUM_QUALITY_ENGINEERING Part 5.1 mandates 9 test categories for every project:
1. Unit tests
2. Integration tests
3. E2E tests
4. Property-based tests (Hypothesis/fast-check)
5. Mutation tests (mutmut/Stryker)
6. Snapshot tests
7. Performance benchmarks
8. Contract tests (API validation)
9. Fuzz tests

Generated projects should have infrastructure for all categories, not just unit tests.

## Tasks

### Test Directory Structure Template
- [ ] Create template for complete test directory:
  ```
  tests/
  ├── unit/
  ├── integration/
  ├── e2e/
  ├── property/
  ├── mutation/
  ├── snapshot/
  ├── performance/
  ├── contract/
  ├── fuzz/
  └── fixtures/
  ```
- [ ] Add README in each directory explaining purpose

### Python Test Templates
- [ ] Create `conftest.py` template with:
  - [ ] Hypothesis profile configuration (ci, dev, debug)
  - [ ] External call prevention fixture
  - [ ] Common fixtures (temp_dir, mock dependencies)
  - [ ] Test naming enforcement
- [ ] Add example unit test following best practices
- [ ] Add example property-based test with Hypothesis
- [ ] Add example performance benchmark with pytest-benchmark
- [ ] Add example snapshot test
- [ ] Configure mutation testing exclusions

### TypeScript Test Templates
- [ ] Create Jest/Vitest configuration for all test types
- [ ] Add example unit test with Jest
- [ ] Add example property-based test with fast-check
- [ ] Add example E2E test with Playwright
- [ ] Add Stryker mutation testing config
- [ ] Add performance benchmark examples

### Test Quality Rules Template
- [ ] Generate test naming convention enforcement
- [ ] Add test organization guidelines (Arrange-Act-Assert)
- [ ] Configure test isolation (no interdependencies)
- [ ] Add test markers/tags for categorization
- [ ] Configure test timeout settings
- [ ] Add randomization with fixed seed

### Coverage Configuration
- [ ] Generate `coverage-thresholds.json` per MAXIMUM_QUALITY_ENGINEERING Part 5.3
- [ ] Set global thresholds (90% lines, 95% functions, 90% branches)
- [ ] Set per-file thresholds (domain 95%, application 90%)
- [ ] Configure mutation score minimum (80%)
- [ ] Add coverage exclusions (test files, generated code)

### Generator Integration
- [ ] Add test generation step in orchestrator
- [ ] Generate test infrastructure during Step 3 (Documentation) or new step
- [ ] Create example tests for generated demo code
- [ ] Ensure tests pass before completing generation
- [ ] Update prompts to emphasize test-first development

### Test Generation Prompts
- [ ] Create prompt for generating unit tests
- [ ] Create prompt for generating property-based tests
- [ ] Create prompt for generating integration tests
- [ ] Instruct Claude on test quality requirements
- [ ] Include examples in prompts

### Validation
- [ ] Verify all 9 test directories created
- [ ] Run initial test suite (should pass)
- [ ] Verify coverage meets thresholds
- [ ] Check mutation testing configured
- [ ] Validate test quality rules enforced

### Documentation
- [ ] Add testing guide to generated README
- [ ] Create TESTING.md with:
  - [ ] How to run each test category
  - [ ] How to write good tests
  - [ ] Property-based testing examples
  - [ ] Mutation testing interpretation
- [ ] Document coverage thresholds and rationale
- [ ] Add testing section to CONTRIBUTING.md

## Acceptance Criteria
- All 9 test categories have infrastructure
- Python projects use Hypothesis for property tests
- TypeScript projects use fast-check
- Mutation testing configured (mutmut/Stryker)
- Performance benchmarks included
- Coverage thresholds enforced (90%+)
- Example tests in each category
- Test quality rules active
- Documentation complete
- Generated projects have passing test suite

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 5
- Issue #67 (Frontend testing infrastructure)
- Issue #81, #82 (Complexity standards context)

## Labels
enhancement, generation, testing

## Dependencies
None - can be implemented independently
