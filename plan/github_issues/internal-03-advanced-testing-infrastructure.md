# Implement Advanced Testing Infrastructure

## Summary
Add property-based testing, mutation testing, performance benchmarks, and other advanced test categories to achieve 9-category test coverage as specified in MAXIMUM_QUALITY_ENGINEERING.md.

## Context
Currently, specinit has primarily unit and integration tests. MAXIMUM_QUALITY_ENGINEERING Part 5.1 specifies 9 test categories:
1. ✅ Unit tests (existing)
2. ✅ Integration tests (existing)
3. ❌ E2E tests (missing)
4. ❌ Property-based tests (missing)
5. ❌ Mutation tests (missing)
6. ❌ Snapshot tests (missing)
7. ❌ Performance tests (missing)
8. ❌ Contract tests (missing - for API validation)
9. ❌ Fuzz tests (missing)

## Tasks

### Property-Based Testing (Hypothesis)
- [ ] Add `hypothesis` to dev dependencies
- [ ] Configure Hypothesis profiles in `conftest.py` (ci, dev, debug)
- [ ] Add property tests for:
  - [ ] Project name validation (valid characters, length limits)
  - [ ] Path handling (no traversal, valid paths)
  - [ ] YAML config serialization/deserialization
  - [ ] Cost calculation with various token counts
  - [ ] Template scoring algorithm
- [ ] Add `--hypothesis-seed=0` to pytest config for reproducibility

### Mutation Testing (mutmut)
- [ ] Add `mutmut` to dev dependencies
- [ ] Create `scripts/mutation-test.sh` script
- [ ] Configure mutation testing exclusions in `pyproject.toml`
- [ ] Run baseline mutation test and document score
- [ ] Set mutation score threshold to 80% (target from plan)
- [ ] Add mutation testing to CI (as optional/advisory initially)

### Performance Benchmarks (pytest-benchmark)
- [ ] Add `pytest-benchmark` to dev dependencies
- [ ] Create `tests/performance/` directory
- [ ] Add benchmark tests for:
  - [ ] Project generation end-to-end
  - [ ] Claude API prompt construction
  - [ ] Template selection algorithm
  - [ ] File writing operations
  - [ ] SQLite history queries
- [ ] Configure benchmark thresholds in `pytest.ini`
- [ ] Add benchmark comparison to CI

### Snapshot Testing (pytest-snapshot)
- [ ] Add `pytest-snapshot` to dev dependencies
- [ ] Create `tests/snapshot/` directory
- [ ] Add snapshot tests for:
  - [ ] Generated pyproject.toml structure
  - [ ] Generated .pre-commit-config.yaml
  - [ ] Generated GitHub workflows
  - [ ] Product spec format
  - [ ] README template output

### E2E Testing
- [ ] Create `tests/e2e/` directory
- [ ] Add E2E test for full project generation flow
- [ ] Add E2E test for GitHub integration workflow
- [ ] Mock Claude API calls with realistic responses
- [ ] Test actual file system operations in temp directories

### Additional Infrastructure
- [ ] Add `pytest-timeout` to prevent hanging tests
- [ ] Add `pytest-randomly` to detect test interdependencies
- [ ] Add `pytest-xdist` for parallel test execution
- [ ] Update test discovery markers in `pyproject.toml`
- [ ] Create `conftest.py` fixture for blocking external calls (Part 5.2)
- [ ] Update `scripts/test.sh` to run all test categories
- [ ] Update CI to run test categories in stages

## Acceptance Criteria
- All 9 test categories have at least one test
- Property-based tests use Hypothesis with configured profiles
- Mutation score measured and tracked (target 80%)
- Performance benchmarks established and tracked
- Snapshot tests detect unintended changes
- E2E tests cover critical user journeys
- Test suite runs in parallel (pytest-xdist)
- All new dependencies documented in CLAUDE.md
- Coverage remains ≥90%

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 5
- Issue #67 (Frontend testing infrastructure)

## Labels
enhancement, testing, quality

## Dependencies
None - can be implemented independently
