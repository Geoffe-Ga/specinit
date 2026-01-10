# GitHub Issues for Maximum Quality Engineering Implementation

This directory contains GitHub issue templates for implementing the Maximum Quality Engineering framework defined in `plan/MAXIMUM_QUALITY_ENGINEERING.md`.

## Overview

The implementation is divided into two major categories:

### A. Internal Quality Improvements (7 issues)
Apply world-class quality standards to the specinit codebase itself.

| Issue | Title | Description |
|-------|-------|-------------|
| internal-01 | Expand Python Quality Tools | Add missing tools: bandit, safety, interrogate, pydocstyle, etc. |
| internal-02 | Comprehensive Pre-Commit Hooks | Full hook suite: security, quality, consistency checks |
| internal-03 | Advanced Testing Infrastructure | 9 test categories: unit, integration, property-based, mutation, etc. |
| internal-04 | Documentation Standards | Google-style docstrings, ADRs, 95% coverage |
| internal-05 | CI/CD Expansion | 7 job categories: quality, tests, mutation, security, etc. |
| internal-06 | Quality Metrics Dashboard | SonarCloud, track 10 mandatory metrics |
| internal-07 | Strengthen Architecture Enforcement | Comprehensive import-linter contracts |

### B. Generation Features (10 issues)
Enable specinit to generate projects with maximum quality from day one.

| Issue | Title | Description |
|-------|-------|-------------|
| generation-01 | Python Quality Template | Complete Python quality stack for generated projects |
| generation-02 | TypeScript Quality Template | Complete TypeScript/ESLint quality stack |
| generation-03 | Comprehensive Test Generation | 9 test categories infrastructure for all projects |
| generation-04 | Security-First Configs | Secret detection, security linting, dependency auditing |
| generation-05 | CI/CD Pipeline Templates | 7-job GitHub Actions workflows |
| generation-06 | Documentation Templates | ADRs, docstrings, comprehensive guides |
| generation-07 | Git Workflow Enforcement | Commitlint, hooks, PR/issue templates |
| generation-08 | Architecture Enforcement Configs | Import-linter, dependency-cruiser setup |
| generation-09 | Subagent Quality Profiles | Quality reviewer, test generator, security auditor agents |
| generation-10 | Quality Dashboard Generation | SonarCloud config, metrics tracking |

### Meta Issue
| Issue | Title | Description |
|-------|-------|-------------|
| meta-00 | Maximum Quality Engineering Roadmap | Epic tracking all 17 sub-issues |

## Creating Issues from Templates

Each markdown file is structured to be passed directly to `gh issue create`. To create an issue:

```bash
# Navigate to repository root
cd /Users/geoffgallinger/Projects/specinit

# Create a single issue
gh issue create --title "Expand Python Quality Tools to World-Class Standards" --body-file plan/github_issues/internal-01-expand-python-quality-tools.md --label enhancement,quality,tooling

# Create all internal issues
for file in plan/github_issues/internal-*.md; do
    title=$(head -n 1 "$file" | sed 's/^# //')
    labels=$(grep "^## Labels" "$file" -A 1 | tail -n 1)
    gh issue create --title "$title" --body-file "$file" --label "$labels"
done

# Create all generation issues
for file in plan/github_issues/generation-*.md; do
    title=$(head -n 1 "$file" | sed 's/^# //')
    labels=$(grep "^## Labels" "$file" -A 1 | tail -n 1)
    gh issue create --title "$title" --body-file "$file" --label "$labels"
done

# Create meta epic
gh issue create --title "EPIC: Maximum Quality Engineering Framework Implementation" --body-file plan/github_issues/meta-00-maximum-quality-engineering-roadmap.md --label epic,quality,enhancement
```

## Implementation Strategy

### Recommended: Sequential Approach
1. **Phase 1**: Implement internal quality improvements (internal-01 through internal-07)
   - Validates framework on specinit itself
   - Provides templates for generation features
   - Team learns all tools and patterns

2. **Phase 2**: Implement generation features (generation-01 through generation-10)
   - Leverage learnings from Phase 1
   - Use specinit's own configs as templates
   - Validate with real project generation

### Alternative: Parallel Approach
- Internal and generation work can proceed simultaneously
- Requires coordination to prevent divergence
- Faster completion but higher coordination overhead

### Incremental Rollout
1. Start with Python (internal-01, generation-01)
2. Add TypeScript (internal + frontend, generation-02)
3. Add advanced testing (internal-03, generation-03)
4. Layer on security, CI/CD, docs
5. Finalize with metrics and dashboards

## Dependencies

### Internal Issues
- `internal-02` depends on `internal-01` (needs tools installed)
- `internal-05` depends on `internal-01`, `internal-03`, `internal-04` (needs tools for CI jobs)
- `internal-06` depends on multiple issues for metrics sources

### Generation Issues
- `generation-05` should coordinate with `generation-01`, `generation-02` (CI for those languages)
- `generation-07` coordinates with `generation-01`, `generation-02` (git hooks)
- `generation-08` coordinates with `generation-01`, `generation-02` (architecture rules)
- `generation-10` depends on `generation-05` (CI integration)

### Cross-Category
- Generation issues can reference specinit's own configurations from internal issues as templates

## Quality Metrics

### Success Criteria for Phase 1 (Internal)
- [ ] All 10 quality metrics tracked
- [ ] Test coverage ≥90%
- [ ] Mutation score ≥80%
- [ ] Documentation coverage ≥95%
- [ ] 0 critical/high security vulnerabilities
- [ ] All 6+ architecture contracts passing
- [ ] CI with 7 job categories
- [ ] Quality dashboard operational

### Success Criteria for Phase 2 (Generation)
- [ ] Generated projects include all quality tools
- [ ] Generated projects have 9 test categories
- [ ] Generated projects have comprehensive CI/CD
- [ ] Generated projects have security scanning
- [ ] Generated projects pass all checks immediately
- [ ] Quality dashboards configured

## Related Issues

### Completed Work
- #81: Python world-class complexity standards ✅
- #70, #71, #75, #77, #78, #80: Complexity improvements

### In Progress
- #82: TypeScript world-class complexity standards
- #67: Frontend testing infrastructure

### Related Epics
- #33: Iterative generation with validation loops
- #34: Auto-suggestions feature
- #51-57: Phase implementations

## References
- **Source Document**: `plan/MAXIMUM_QUALITY_ENGINEERING.md`
- **Specinit Docs**: `CLAUDE.md`, `AGENTS.md`
- **Current Configs**: `.pre-commit-config.yaml`, `pyproject.toml`, `.importlinter`, etc.

## Timeline Estimate
- **Phase 1 (Internal)**: 4-6 weeks
- **Phase 2 (Generation)**: 6-8 weeks
- **Total**: 10-14 weeks for complete implementation

## Notes
- Issue templates include task checklists for granular tracking
- Each issue has clear acceptance criteria
- Dependencies documented to prevent blocking
- Labels suggest: enhancement, quality, testing, security, ci-cd, documentation, architecture, etc.
