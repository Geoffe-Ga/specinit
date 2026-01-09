# Generate Git Workflow Enforcement Configuration

## Summary
Implement generation of git hooks, commit message validation, and branch protection configurations from MAXIMUM_QUALITY_ENGINEERING.md Part 7.

## Context
Generated projects should enforce conventional commits, validate commit messages, run quality checks before push, and configure branch protection rules.

## Tasks

### Commitizen/Commitlint Setup
- [ ] Add commitizen to dev dependencies (Python/Node.js)
- [ ] Create `commitlint.config.js` template (lines 1650-1672)
- [ ] Configure conventional commit types
- [ ] Set commit message format rules:
  - [ ] type-enum enforcement
  - [ ] scope-case (kebab-case)
  - [ ] subject-case (no sentence-case, start-case, pascal-case, upper-case)
  - [ ] subject-empty (never)
  - [ ] subject-full-stop (never '.')
  - [ ] header-max-length (72)
  - [ ] body-max-line-length (100)
- [ ] Add commitizen to pre-commit/husky hooks

### Git Hooks (Python projects)
- [ ] Configure pre-commit hooks (already in generation-01)
- [ ] Add commit-msg hook for commitizen
- [ ] Add pre-push hook to run tests
- [ ] Add prepare-commit-msg for commit template

### Git Hooks (Node.js projects)
- [ ] Add Husky configuration
- [ ] Create `.husky/pre-commit` script
- [ ] Create `.husky/pre-push` script
- [ ] Create `.husky/commit-msg` script
- [ ] Create `.husky/prepare-commit-msg` script
- [ ] Configure lint-staged for selective file checks

### Commit Message Template
- [ ] Create `.gitmessage` template with:
  - [ ] Conventional commit format
  - [ ] Type options (feat, fix, docs, etc.)
  - [ ] Scope examples
  - [ ] Body and footer guidelines
- [ ] Configure git to use template
- [ ] Add instructions in CONTRIBUTING.md

### Branch Protection Documentation
- [ ] Create `docs/git-workflow.md` documenting:
  - [ ] Conventional commit format
  - [ ] Branch naming conventions
  - [ ] Recommended branch protection rules (lines 1676-1688):
    - [ ] Require PR reviews (minimum 1)
    - [ ] Dismiss stale reviews
    - [ ] Require CODEOWNERS review
    - [ ] Require status checks to pass
    - [ ] Require branches up to date
    - [ ] Require signed commits
    - [ ] Require linear history
    - [ ] Include administrators
    - [ ] Block force pushes
    - [ ] Block deletions
  - [ ] GitHub repository settings instructions

### CODEOWNERS Template
- [ ] Create `.github/CODEOWNERS` template
- [ ] Add examples for different paths
- [ ] Document ownership syntax
- [ ] Add to generated projects

### Pull Request Template
- [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] Include sections:
  - [ ] Summary/Description
  - [ ] Type of Change (feature, fix, docs, etc.)
  - [ ] Testing Done
  - [ ] Checklist (tests added, docs updated, etc.)
  - [ ] Breaking Changes
  - [ ] Related Issues
- [ ] Add quality check reminders

### Issue Templates
- [ ] Create `.github/ISSUE_TEMPLATE/` directory
- [ ] Add bug_report.md template
- [ ] Add feature_request.md template
- [ ] Add question.md template
- [ ] Configure issue template chooser

### Generator Integration
- [ ] Generate git workflow configs during Step 4 (Developer Tooling)
- [ ] Install commitizen/commitlint during setup
- [ ] Configure git hooks (pre-commit/husky)
- [ ] Create CODEOWNERS file
- [ ] Generate PR and issue templates
- [ ] Add git workflow documentation
- [ ] Test commit message validation works

### Validation
- [ ] Verify commitlint configuration valid
- [ ] Test commit-msg hook rejects invalid commits
- [ ] Check PR template rendered correctly
- [ ] Validate issue templates work
- [ ] Ensure CODEOWNERS syntax correct

### Documentation
- [ ] Add git workflow section to README
- [ ] Update CONTRIBUTING.md with:
  - [ ] Commit message format
  - [ ] Branch naming conventions
  - [ ] PR process
  - [ ] Issue creation guidelines
- [ ] Document how to bypass hooks (emergencies only)

## Acceptance Criteria
- Commitlint configured with conventional commits
- Git hooks installed and active
- Commit-msg hook validates format
- Pre-push hook runs tests
- `.gitmessage` template configured
- CODEOWNERS file present
- PR template comprehensive
- Issue templates for bug/feature/question
- Branch protection rules documented
- Git workflow documented in CONTRIBUTING.md
- Invalid commits rejected by hook

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 7
- Issue internal-02 (Pre-commit hooks for specinit)

## Labels
enhancement, generation, git, workflow

## Dependencies
- Coordinated with generation-01 (Python) and generation-02 (TypeScript)
