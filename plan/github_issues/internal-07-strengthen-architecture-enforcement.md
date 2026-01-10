# Strengthen Architecture Enforcement with Comprehensive Rules

## Summary
Expand `.importlinter` configuration to enforce domain-driven design principles and prevent architectural violations as specified in MAXIMUM_QUALITY_ENGINEERING.md Part 4.1.

## Context
Current `.importlinter` has 6 contracts. MAXIMUM_QUALITY_ENGINEERING Part 4.1 provides a template for comprehensive architectural enforcement including:
- Domain layer independence
- Layered architecture enforcement
- Circular dependency prevention
- Module-specific rules

## Tasks

### Review Current Architecture
- [ ] Document current specinit architecture layers:
  - CLI layer (user interface)
  - Server layer (FastAPI web interface)
  - Generator layer (orchestration and prompts)
  - Storage layer (config, history, keyring)
  - GitHub layer (GitHub integration)
- [ ] Identify intended dependency flow
- [ ] Document architectural principles in ADR

### Expand Import Rules
- [ ] Add independence contract for core layers
  - [ ] CLI should not import from Server
  - [ ] Generator should not import from CLI or Server
  - [ ] Storage should not import from CLI, Server, or Generator
  - [ ] GitHub should not import from CLI or Server
- [ ] Add layers contract enforcing:
  - [ ] CLI/Server → Generator → Storage (unidirectional)
  - [ ] GitHub is parallel to Generator (service layer)
- [ ] Add forbidden circular dependency rules
- [ ] Add contract forbidding test imports in production code
- [ ] Add contract ensuring utils/common don't import from features

### Additional Constraints
- [ ] Prevent `generator/` from importing FastAPI (server concern)
- [ ] Prevent `cli/` from importing `server/` modules
- [ ] Ensure `storage/` is pure data layer (no business logic)
- [ ] Validate that `prompts.py` has no external service dependencies

### Tooling
- [ ] Add pydeps to dev dependencies
- [ ] Create `scripts/check-architecture.sh`
- [ ] Add architecture visualization generation
- [ ] Add architecture check to CI (Job 6)
- [ ] Add architecture check to pre-commit hooks

### Documentation
- [ ] Create architecture diagram in `docs/architecture/`
- [ ] Document layer responsibilities
- [ ] Document import rules and rationale
- [ ] Add architecture section to CONTRIBUTING.md
- [ ] Write ADR for architecture enforcement decisions

## Acceptance Criteria
- `.importlinter` has comprehensive contracts for all layers
- Architecture violations fail CI
- `scripts/check-architecture.sh` validates all contracts
- `pydeps` generates architecture visualization
- Architecture diagram exists and is current
- No circular dependencies exist
- All architectural rules documented
- CONTRIBUTING.md explains architecture constraints

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 4.1
- Current `.importlinter` configuration

## Labels
enhancement, architecture, quality

## Dependencies
- Requires internal-04 (for ADR infrastructure)
