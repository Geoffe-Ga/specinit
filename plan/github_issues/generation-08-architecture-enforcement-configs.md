# Generate Architecture Enforcement Configurations

## Summary
Implement generation of import-linter (Python) and dependency-cruiser (TypeScript) configurations to enforce architectural boundaries in generated projects, based on MAXIMUM_QUALITY_ENGINEERING.md Part 4.

## Context
Generated projects should have automated enforcement of architectural layers, dependency rules, and prevent circular dependencies from day one.

## Tasks

### Python: Import-Linter Configuration
- [ ] Create `.importlinter` template based on Part 4.1 (lines 1278-1309)
- [ ] Define default layer structure:
  - [ ] Presentation/API layer
  - [ ] Application/Service layer
  - [ ] Domain/Business layer
  - [ ] Infrastructure/Data layer
- [ ] Add contract types:
  - [ ] Independence contract (domain independence)
  - [ ] Layers contract (unidirectional dependencies)
  - [ ] Forbidden contract (no circular dependencies)
- [ ] Make contracts configurable by project type:
  - [ ] Web API: presentation → application → domain → infrastructure
  - [ ] CLI: cli → core → storage
  - [ ] Library: public → internal → private
- [ ] Add import-linter to dev dependencies
- [ ] Add to pre-commit hooks

### TypeScript: Dependency-Cruiser Configuration
- [ ] Create `.dependency-cruiser.js` template based on Part 4.2 (lines 1313-1398)
- [ ] Add forbidden rules:
  - [ ] no-circular dependencies (error)
  - [ ] no-orphans (error)
  - [ ] domain-independence (domain can't import from other layers)
  - [ ] application-layer-rules (application can't import presentation)
  - [ ] no-deprecated-packages (error)
  - [ ] no-dev-deps-in-production (error)
- [ ] Configure for TypeScript projects
- [ ] Add module resolution settings
- [ ] Include visualization capabilities
- [ ] Add to CI workflow

### Architecture Documentation Template
- [ ] Create `docs/architecture/layers.md` documenting:
  - [ ] Layer definitions and responsibilities
  - [ ] Dependency rules and rationale
  - [ ] Examples of correct/incorrect dependencies
  - [ ] Architectural patterns used
- [ ] Generate architecture diagram
- [ ] Add to README

### Madge Integration (TypeScript)
- [ ] Add madge for circular dependency detection
- [ ] Create script to generate dependency graph
- [ ] Add to CI workflow
- [ ] Configure visualization output

### Pydeps Integration (Python)
- [ ] Add pydeps for dependency visualization
- [ ] Create script to check for circular dependencies
- [ ] Add to CI workflow
- [ ] Configure output format

### Project Type Templates
- [ ] Web API architecture template:
  - [ ] routes → services → repositories → models
  - [ ] No routes importing repositories directly
- [ ] CLI architecture template:
  - [ ] cli → commands → core → storage
  - [ ] cli layer can't import storage directly
- [ ] Library architecture template:
  - [ ] public API → internal → private
  - [ ] public can't import private directly
- [ ] Microservice architecture template:
  - [ ] api → application → domain → infrastructure
  - [ ] domain completely independent

### Generator Integration
- [ ] Detect project type during generation
- [ ] Select appropriate architecture template
- [ ] Generate architecture configuration during Step 4
- [ ] Create initial architecture documentation
- [ ] Add architecture validation to CI
- [ ] Update prompts to follow architecture rules
- [ ] Ensure generated code respects layer boundaries

### Quality Gates
- [ ] Add architecture check to pre-commit
- [ ] Add to CI as required check
- [ ] Fail builds on violations
- [ ] Generate violation reports

### Visualization
- [ ] Generate architecture diagrams automatically
- [ ] Create dependency graphs
- [ ] Add to documentation
- [ ] Update on significant changes

### Validation
- [ ] Verify configuration files valid
- [ ] Test architecture rules work
- [ ] Check violations detected correctly
- [ ] Ensure CI integration working
- [ ] Validate generated projects respect rules

### Documentation
- [ ] Add architecture section to README
- [ ] Create architecture guide in docs/
- [ ] Document how to modify rules
- [ ] Add troubleshooting for violations
- [ ] Update CONTRIBUTING.md with architecture constraints

## Acceptance Criteria
- Python projects have import-linter configured
- TypeScript projects have dependency-cruiser configured
- Architecture layers defined for project type
- Circular dependencies blocked
- Layer violations detected and blocked
- Architecture documentation generated
- Dependency graphs visualized
- CI enforces architecture rules
- Pre-commit hooks check architecture
- Documentation explains rules and rationale

## References
- plan/MAXIMUM_QUALITY_ENGINEERING.md Part 4
- Issue internal-07 (Architecture enforcement for specinit)
- .importlinter (specinit's own configuration)

## Labels
enhancement, generation, architecture

## Dependencies
- Coordinated with generation-01 (Python) and generation-02 (TypeScript)
