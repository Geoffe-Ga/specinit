# Implement Quality-Focused Subagent Profiles

## Summary
Create specialized Claude Code agent profiles for quality enforcement in generated projects, based on MAXIMUM_QUALITY_ENGINEERING.md Part 8.

## Context
MAXIMUM_QUALITY_ENGINEERING Part 8 defines three specialized agent profiles:
1. Quality Reviewer Agent - Ruthless code review
2. Test Generator Agent - Comprehensive test creation
3. Security Auditor Agent - Security-first validation

These profiles should be embedded in generated projects to guide AI-assisted development.

## Tasks

### Quality Reviewer Agent Profile
- [ ] Create `.claude/profiles/quality-reviewer.md` template (lines 1695-1746)
- [ ] Include comprehensive review checklist:
  - [ ] Code Quality (functions <50 lines, complexity <10, no magic numbers, etc.)
  - [ ] Testing (edge cases, error paths, specific assertions)
  - [ ] Security (no secrets, input validation, injection prevention)
  - [ ] Architecture (SOLID principles, dependency flow)
  - [ ] Documentation (public APIs, complex logic, examples)
- [ ] Define response format (specific line numbers, code suggestions)
- [ ] Add "never say looks good without explanation" rule

### Test Generator Agent Profile
- [ ] Create `.claude/profiles/test-generator.md` template (lines 1749-1793)
- [ ] Define test generation principles:
  - [ ] Start with failure modes
  - [ ] Test behavior, not implementation
  - [ ] Use property-based testing for appropriate cases
  - [ ] Follow test naming convention: `test_<unit>_<scenario>_<expected_outcome>`
  - [ ] Mandatory test categories per feature
- [ ] Include test quality rules
- [ ] Add examples of good test patterns

### Security Auditor Agent Profile
- [ ] Create `.claude/profiles/security-auditor.md` template (lines 1796-1843)
- [ ] Include security audit checklist:
  - [ ] Authentication & Authorization
  - [ ] Data Protection (encryption at rest/transit)
  - [ ] Input Validation (whitelist-based)
  - [ ] Dependencies (trusted sources, pinned versions)
  - [ ] Error Handling (no information leakage)
- [ ] Add common vulnerabilities to check:
  - [ ] OWASP Top 10
  - [ ] CWE Top 25
  - [ ] Language-specific issues

### CLAUDE.md Integration
- [ ] Generate project-specific CLAUDE.md with:
  - [ ] Critical rules from MAXIMUM_QUALITY_ENGINEERING
  - [ ] Project-specific context
  - [ ] Quality standards and thresholds
  - [ ] Tool usage instructions
  - [ ] Common tasks and workflows
  - [ ] Reference to agent profiles
- [ ] Adapt content to project type and language

### AGENTS.md Generation
- [ ] Create AGENTS.md with:
  - [ ] Overview of quality requirements
  - [ ] How to use agent profiles
  - [ ] Quality gates and thresholds
  - [ ] Development workflow
  - [ ] Provider-agnostic instructions

### Agent Profile Activation
- [ ] Add profile invocation examples to documentation
- [ ] Create npm/pip scripts to run profiles
- [ ] Integrate profiles with IDE extensions
- [ ] Add profile selection to CLI tools

### Generator Integration
- [ ] Generate `.claude/` directory structure
- [ ] Create all three agent profiles during Step 3 (Documentation)
- [ ] Generate CLAUDE.md with project context
- [ ] Generate AGENTS.md for provider-agnostic use
- [ ] Update main README to reference profiles
- [ ] Add profile usage examples

### Profile Customization
- [ ] Make profiles customizable per project type
- [ ] Add language-specific checks
- [ ] Include framework-specific patterns
- [ ] Allow users to extend profiles

### Documentation
- [ ] Add agent profiles section to README
- [ ] Document how to invoke profiles
- [ ] Provide examples of profile usage
- [ ] Add troubleshooting guide

### Validation
- [ ] Test profiles with Claude Code
- [ ] Verify checklist completeness
- [ ] Ensure profiles enforce quality standards
- [ ] Validate CLAUDE.md generation

## Acceptance Criteria
- Three agent profiles generated in `.claude/profiles/`
- CLAUDE.md generated with project-specific context
- AGENTS.md generated for provider-agnostic use
- Profiles include comprehensive checklists
- Profiles match MAXIMUM_QUALITY_ENGINEERING standards
- Documentation explains profile usage
- Profiles customized by project type
- Examples of profile invocation included

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 8, Part 12
- CLAUDE.md, AGENTS.md (specinit's own files as examples)

## Labels
enhancement, generation, ai, quality

## Dependencies
None - can be implemented independently
