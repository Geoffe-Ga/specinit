SpecInit Product Specification
Version: 1.0.1
Created: December 13, 2025
Updated: December 13, 2025
Project Type: Local-first CLI tool with web UI for AI-powered project initialization

Executive Summary
SpecInit is a local-first command-line tool that transforms project ideas into working codebases in minutes. Users answer 5 simple questions through a web interface, and the tool orchestrates Claude API calls to generate a complete project structure with documentation, tests, configuration files, and demo code—all following best practices like TDD, linting, and comprehensive documentation.
Core Value Proposition: Reduce project initialization from 3 hours of manual setup to 3 minutes of guided configuration.

User Story
Primary User Story:
As a software developer
I want to quickly bootstrap new projects with best practices baked in
So that I can focus on building features instead of configuring tooling
Secondary User Stories:

As a developer learning new tech stacks, I want comprehensive examples so I can understand best practices
As a developer who forgets git commands, I want automatic repository setup so I don't have to look up syntax
As a cost-conscious developer, I want to see API costs upfront so I can budget appropriately


Core Features
1. Interactive Web-Based Configuration

Local web server with clean, simple form interface
5-question workflow to capture project requirements
Real-time validation and smart defaults
No account creation or external services required

2. Multi-Platform Project Generation

Support for common platform combinations (Web, iOS, Android, CLI)
Intelligent tech stack suggestions based on platform selection
Template system for different project types

3. AI-Orchestrated Code Generation

Automated 8-step generation process using Claude API
Progress tracking visible in both terminal and browser
Comprehensive output including docs, tests, and configs
Cost transparency (show estimated and actual API costs)

4. Best Practices Enforcement

Test-Driven Development setup with working tests
Pre-commit hooks and linter configurations
CI/CD pipeline templates
Git initialization with detailed commit messages

5. Local-First Architecture

API keys stored locally and encrypted
No telemetry or data collection
Offline template library
Privacy-preserving design


Technical Architecture
Technology Stack
Backend:

Python 3.11+
Click (CLI framework)
FastAPI (local web server)
Anthropic Python SDK
Jinja2 (template engine)

Frontend:

React 18
Vite (build tool)
Tailwind CSS
React Hook Form

Storage:

SQLite (local project history and preferences)
YAML (configuration and templates)

Distribution:

PyPI package (pip install specinit)
Optional Docker image for non-Python users

System Components
┌─────────────────────────────────────────────┐
│           User (Developer)                   │
└──────────────┬──────────────────────────────┘
               │
               ├─► CLI (Click)
               │   ├─ init (setup API key)
               │   ├─ new (start generation)
               │   ├─ list (show history)
               │   └─ config (manage settings)
               │
               ├─► Local Web Server (FastAPI)
               │   ├─ Serve React UI
               │   ├─ Handle form submission
               │   ├─ WebSocket for progress
               │   └─ API endpoints
               │
               ├─► Generator Engine
               │   ├─ Template Selector
               │   ├─ Prompt Builder
               │   ├─ Claude Orchestrator
               │   └─ File Writer
               │
               └─► Storage Layer
                   ├─ SQLite (history)
                   ├─ YAML configs
                   └─ Templates

Detailed Feature Specifications
Feature 1: Configuration Workflow
Question 1: Target Platforms

Component: Multi-select checkbox grid with icons
Options: Web, iOS, Android, Desktop, Apple Watch, Samsung Watch, CLI, API/Backend
Validation: At least one platform must be selected
Smart behavior: Suggest cross-platform frameworks when multiple platforms selected

Question 2: Core User Story

Component: Three linked text inputs with example overlay
Fields: Role (who), Action (what), Outcome (why)
Validation: Each field minimum 3 characters
Smart behavior: Claude analyzes this to infer data models and auth needs

Question 3: Feature List

Component: Dynamic list with autocomplete
Behavior:

Add up to 10 features
Autocomplete suggests common features based on user story
Each feature can be reordered or removed


Validation: At least 1 feature required, max 10 features
Example suggestions: "User authentication", "Dark mode", "Offline support", "Push notifications"

Question 4: Tech Stack & Tools

Component: Grouped multi-select with smart filtering
Categories: Frontend, Backend, Database, Tools
Behavior:

Filter options based on selected platforms
Show compatibility warnings
Highlight recommended combinations


Validation: Must select at least one backend framework if not CLI-only

Question 5: UX Aesthetic Principles

Component: Tag selector (max 3 selections)
Options: Minimalist, Professional, Playful, Accessible-First, High-Contrast, Retro, Modern
Behavior: Shows small preview or description on hover
Validation: Maximum 3 selections
Smart behavior: Influences color palette and component choices

Feature 2: 8-Step Generation Process
Step 1: Product Specification Generation

Input: User's 5 answers + TDD emphasis prompt
Claude generates comprehensive product spec with phases
Output: plan/product-spec.md (markdown file)
Includes: Requirements, architecture, data models, test strategy
Cost estimate: ~$0.10-0.30

Step 2: Project Structure Creation

Input: Product spec
Claude generates shell script to create all files/directories
Output: init-structure.sh script
Executes script to create skeleton
Cost estimate: ~$0.05-0.10

Step 3: Documentation Generation

Input: Product spec + project structure
Claude writes README, CONTRIBUTING, CLAUDE.md
Output: Comprehensive documentation in /docs
Includes: Architecture overview, repo tour, setup instructions
Cost estimate: ~$0.15-0.40

Step 4: Developer Tooling Configuration

Input: Tech stack selection + best practices requirements
Claude generates linter configs, pre-commit hooks, CI/CD pipelines
Output: .eslintrc, .prettierrc, .pre-commit-config.yaml, .github/workflows/
All tools configured to work together
Cost estimate: ~$0.10-0.25

Step 5: Validation & Testing Setup

Execute linters and validate all configs
Ensure pre-commit hooks install correctly
Verify directory structure matches spec
Output: Validation report in terminal
No Claude API calls (local validation)

Step 6: Dependency Installation

Install all dependencies based on tech stack
Run initial linter checks
Verify all tools are working
Output: Installation logs
No Claude API calls (local npm/pip/etc)

Step 7: Git Initialization

Initialize git repository
Create comprehensive .gitignore
Initial commit with detailed message including user story and features
Output: Git repository with history
No Claude API calls (local git operations)

Step 8: Demo Implementation

Input: Complete context (spec, structure, tech stack)
Claude generates working demo code with tests
Output: Runnable application in src/ with passing tests in tests/
Includes: Basic routing, example components, API endpoints, database models
Cost estimate: ~$0.80-2.00

Total estimated cost per project: $1.20-3.05
Feature 3: Progress Tracking
Browser Interface:
┌─────────────────────────────────────────────────┐
│  Generating: My Awesome App                     │
│                                                  │
│  ✓ Product specification created                │
│  ✓ Project structure generated                  │
│  ✓ Documentation written                        │
│  ✓ Developer tooling configured                 │
│  ⏳ Installing dependencies...        [47%]     │
│  ⏱ Git initialization                           │
│  ⏱ Generating demo code                         │
│  ⏱ Final validation                             │
│                                                  │
│  Estimated time remaining: 1m 32s                │
│  API cost so far: $0.73                         │
└─────────────────────────────────────────────────┘
Terminal Interface:
[specinit] Starting project generation
[specinit] Project: my-awesome-app
[specinit] Estimated cost: $1.50-2.50

[claude] Step 1: Generating product specification...
[claude] ✓ Tokens: 2,341 in / 7,892 out ($0.21)
[specinit] ✓ Wrote plan/product-spec.md

[claude] Step 2: Creating project structure...
[claude] ✓ Tokens: 3,124 in / 1,456 out ($0.08)
[specinit] ✓ Created 34 files in 8 directories

[claude] Step 3: Writing documentation...
[claude] ✓ Tokens: 4,567 in / 9,234 out ($0.31)
[specinit] ✓ Wrote README.md, CONTRIBUTING.md, CLAUDE.md

...

[specinit] ✓ Project complete!
[specinit] Location: ./my-awesome-app
[specinit] Total cost: $1.87
[specinit] 
[specinit] Next steps:
           cd my-awesome-app
           npm run dev
Feature 4: Configuration Management
Config File Location: ~/.specinit/config.yaml
Config Structure:
yamlapi:
  provider: anthropic
  api_key: <encrypted>
  model: claude-sonnet-4-5-20250929
  max_tokens: 100000

preferences:
  auto_open_editor: vscode  # or cursor, idea, none
  auto_git_init: true
  show_cost_warnings: true
  cost_limit: 5.00  # fail if exceeds this

usage:
  projects_created: 7
  total_cost: 12.34
  last_used: "2025-12-13T10:30:00Z"
CLI Commands:

specinit config show - Display current config
specinit config set api_key <key> - Update API key
specinit config set cost_limit 10.00 - Update cost limit
specinit config reset - Reset to defaults

Feature 5: Template System
Template Structure:
yaml# ~/.specinit/templates/react-fastapi.yaml
name: "React + FastAPI Web App"
description: "Full-stack web application with React frontend and FastAPI backend"
platforms: [web]
tech_stack:
  frontend: [react, typescript, vite, tailwind]
  backend: [fastapi, python, uvicorn]
  database: [postgresql, sqlalchemy]
  tools: [pytest, eslint, prettier]

directory_structure:
  - frontend/src/
  - frontend/src/components/
  - frontend/src/pages/
  - backend/app/
  - backend/app/api/
  - backend/app/models/
  - backend/tests/
  - docs/

recommended_features:
  - User authentication
  - API documentation (Swagger)
  - Database migrations
  - CORS configuration
```

**Included Templates (MVP):**
1. `react-fastapi` - React + FastAPI web app
2. `react-native` - React Native mobile app (iOS/Android)
3. `nextjs` - Next.js web app with API routes
4. `python-cli` - Python CLI tool with Click
5. `fastapi-only` - API backend only

---

## File Output Structure

Every generated project follows this structure:
```
<project-name>/
├── plan/
│   ├── product-spec.md           # Comprehensive spec from Step 1
│   ├── progress-notes.md         # Updated after each phase
│   └── audit-log.md              # Self-audit results
│
├── docs/
│   ├── README.md                 # User-facing documentation
│   ├── CONTRIBUTING.md           # Contribution guidelines
│   ├── CLAUDE.md                 # AI context for future work
│   └── architecture/
│       ├── overview.md           # System architecture
│       ├── data-models.md        # Database/data structures
│       └── repo-tour.md          # Guided tour of codebase
│
├── .github/
│   └── workflows/
│       ├── ci.yml                # Continuous integration
│       └── lint.yml              # Code quality checks
│
├── src/                          # Application source code
│   └── (framework-specific structure)
│
├── tests/                        # Test suite
│   └── (framework-specific tests)
│
├── .specinit.yaml               # Metadata about generation
├── .gitignore                    # Comprehensive ignore rules
├── .eslintrc.js                  # ESLint configuration
├── .prettierrc                   # Prettier configuration
├── .pre-commit-config.yaml       # Pre-commit hooks
├── package.json                  # or requirements.txt, Cargo.toml, etc
└── README.md                     # Quick start guide

Development Phases
Phase 1: Core Functionality (Weeks 1-2)
Deliverables:

 CLI with init, new, list, config commands
 Local FastAPI server with WebSocket support
 React form UI with 5-question workflow
 Template system with 2 templates (react-fastapi, python-cli)
 Steps 1-7 implementation
 Basic Step 8 implementation
 Config management with encrypted API key storage
 Cost estimation and tracking

Testing Requirements:

Unit tests for all generator functions
Integration test: Full generation flow for react-fastapi template
Manual validation: Generate project, verify it runs

Commit Strategy:

Commit after each major component (CLI, server, UI, templates)
Use conventional commits: feat:, fix:, docs:, test:

Progress Tracking:

Update plan/progress-notes.md after completing each deliverable
Audit against this spec after Phase 1 completion

Success Criteria:

Can generate working React+FastAPI project
All linters pass on generated code
All tests pass on generated code
Total generation time < 5 minutes
API cost < $3.00 per project

Phase 2: Polish & Expansion (Week 3)
Deliverables:

 Add 2 more templates (react-native, nextjs)
 Improve error handling and recovery
 Add progress persistence (resume if interrupted)
 Better cost warnings and limits
 Comprehensive README and documentation
 Installation testing on fresh machine

Testing Requirements:

Test all 4 templates end-to-end
Test error scenarios (API key invalid, rate limited, etc)
Test on macOS, Linux, Windows

Commit Strategy:

One commit per template addition
Document breaking changes in commit messages

Progress Tracking:

Update plan/progress-notes.md with lessons learned
Performance audit: Identify slowest steps

Success Criteria:

All 4 templates working
Graceful error messages
Works on all platforms
Documentation is clear for first-time users

Phase 3: Release Preparation (Week 4)
Deliverables:

 PyPI package setup
 Demo video (3-5 minutes)
 Example generated projects in /examples
 CONTRIBUTING.md for potential contributors
 GitHub Issues templates
 MIT License

Testing Requirements:

Test pip install specinit from TestPyPI
External beta test with 3-5 developers
Gather feedback and fix critical issues

Commit Strategy:

Tag release commits: v1.0.0
Changelog generation

Progress Tracking:

Final audit against original spec
Document deviations and reasons in plan/audit-log.md

Success Criteria:

PyPI package installs cleanly
Beta testers successfully generate projects
Zero critical bugs
Ready for public launch


Prompt Engineering Strategy
Master Prompt Template
All Claude API calls use variations of this base prompt:
markdownYou are an expert software architect specializing in project initialization and best practices.

# Context
The user wants to create a new software project with these requirements:
{user_requirements}

# Your Task
{specific_step_instructions}

# Critical Guidelines
1. **Test-Driven Development**: Write tests FIRST, then implementation
2. **No Shortcuts**: Never comment out failing tests or skip validation
3. **Documentation**: Update docs with every code change
4. **Best Practices**: Follow industry standards for chosen tech stack
5. **Conventional Commits**: Use clear, descriptive commit messages
6. **Completeness**: All code must be production-ready, not TODOs

# Planning Directory
All planning and specification documents should be saved in the /plan/ directory:
- product-spec.md - Comprehensive project specification
- progress-notes.md - Development progress tracking
- audit-log.md - Quality and compliance audits

# Output Format
{specific_output_format}

# Quality Checklist
Before finishing, verify:
- [ ] All tests pass
- [ ] All linters pass
- [ ] Documentation is comprehensive
- [ ] Code follows best practices for {tech_stack}
- [ ] No placeholder/TODO comments
- [ ] Planning documents saved in /plan/ directory
Step-Specific Prompts
Step 1 (Product Spec):

Emphasize phases and TDD
Request markdown artifact with specific sections
Include self-audit checklist
Output to: plan/product-spec.md

Step 2 (Structure):

Request executable bash script
Must create all directories and touch all files
Include comments explaining structure
Must create: plan/ directory for planning documents

Step 3 (Documentation):

README: Quick start, features, architecture overview
CONTRIBUTING: Setup, workflow, testing, PR process
CLAUDE.md: AI context, key decisions, gotchas
Note: These go in /docs, not /plan

Step 4 (Tooling):

Request working configs, not examples
All tools must integrate (e.g., ESLint + Prettier compatible)
Include pre-commit hooks that actually work

Step 8 (Demo Code):

Request minimal but complete implementation
Must demonstrate all key features from user's list
Tests must pass without modification
Code must run without additional setup
Update plan/progress-notes.md with implementation notes


Testing Strategy
Unit Tests
Test Coverage Requirements:

CLI commands: 80%+ coverage
Generator functions: 90%+ coverage
Template system: 85%+ coverage
Config management: 90%+ coverage
UI components: 50%+ coverage (UI tests are flaky, lower bar)

Key Test Cases:
python# Test CLI
def test_init_creates_config_file()
def test_new_without_api_key_fails()
def test_list_shows_project_history()

# Test Generator
def test_template_selection_for_web_platform()
def test_prompt_builder_includes_all_user_inputs()
def test_cost_estimation_within_range()
def test_plan_directory_created()

# Test Templates
def test_react_fastapi_template_has_required_files()
def test_template_validates_platform_compatibility()
def test_generated_project_has_plan_directory()

# Test Config
def test_api_key_encryption()
def test_config_file_permissions()

# Test UI (50% coverage target)
def test_form_renders_all_questions()
def test_form_validation_prevents_submission()
def test_platform_selection_updates_tech_stack_options()
```

### Integration Tests

**End-to-End Flows:**
1. Fresh install → init → new project → verify runs
2. Invalid API key → appropriate error message
3. Cost exceeds limit → graceful failure
4. Interrupted generation → resume capability
5. Verify `plan/` directory structure in generated projects

**Test Approach:**
- Use temporary directories for all file operations
- Mock Anthropic API calls for reproducibility
- Verify generated files against expected structure
- Check for `plan/` directory and its contents
- Actually run `npm install` and `npm test` on output

### Manual Testing Checklist

Before each phase completion:
- [ ] Generate project with each template
- [ ] Verify `plan/` directory exists with all expected files
- [ ] Run `npm install` or equivalent
- [ ] Run `npm test` or equivalent (must pass)
- [ ] Run linters (must pass)
- [ ] Verify documentation is accurate
- [ ] Check git history is clean
- [ ] Confirm `plan/product-spec.md` is comprehensive
- [ ] Confirm total cost is reasonable

---

## Error Handling

### Expected Errors

**API-Related:**
- Invalid API key → Clear message with link to setup docs
- Rate limited → Wait and retry with exponential backoff (max 3 attempts)
- Cost exceeds limit → Stop generation, show partial progress
- Network error → Retry with user confirmation

**File System:**
- Directory already exists → Ask user to confirm overwrite
- Permission denied → Show clear error with fix suggestion
- Disk full → Fail gracefully with cleanup

**Generation:**
- Linters fail on generated code → Claude auto-fixes (max 2 attempts)
- Tests fail on generated code → Claude debugs and fixes (max 2 attempts)
- After 2 failed fix attempts → Show error, ask user if they want to continue

### Error Message Examples

**Good Error Messages:**
```
[specinit] ✗ API key invalid or expired
[specinit] 
[specinit] Please update your API key:
[specinit]   specinit config set api_key YOUR_KEY
[specinit] 
[specinit] Get an API key: https://console.anthropic.com/
```
```
[specinit] ✗ Generation cost would exceed your limit
[specinit] 
[specinit] Estimated cost: $3.20
[specinit] Your limit: $3.00
[specinit] 
[specinit] Options:
[specinit]   1. Increase limit: specinit config set cost_limit 5.00
[specinit]   2. Simplify project (fewer features)
[specinit]   3. Continue anyway: specinit new --ignore-cost-limit
```

---

## Performance Requirements

### Response Time Targets

- CLI command startup: < 500ms
- Web UI loads: < 2s
- Form submission validation: < 100ms
- Total generation time: < 5 minutes (for typical project)
  - Step 1: ~30s
  - Step 2: ~10s
  - Step 3: ~45s
  - Step 4: ~30s
  - Step 5-7: ~60s (mostly local operations)
  - Step 8: ~120s

### Resource Constraints

- Memory usage: < 500MB during generation
- Disk space: < 50MB for specinit installation
- Generated project size: 50-500MB (depends on dependencies)

---

## Security & Privacy

### API Key Management

- Store encrypted using OS keyring (keyring library)
- Never log API keys
- Config file permissions: 600 (user read/write only)
- Support environment variable: `SPECINIT_API_KEY`

### Data Collection

**What we DO NOT collect:**
- User's project details
- Generated code
- API usage patterns
- Telemetry of any kind

**What we DO store locally:**
- Project history (name, date, cost) in SQLite
- User preferences
- Template cache

**Privacy Principle:** Everything stays on user's machine

---

## Success Metrics

### Internal Metrics (for development)

- **Generation Success Rate:** > 95% (projects that generate without errors)
- **Test Pass Rate:** > 90% (generated tests pass on first run)
- **Lint Pass Rate:** > 95% (generated code passes linters)
- **Cost Accuracy:** Estimated cost within 20% of actual
- **Generation Speed:** 90% of projects complete in < 5 minutes
- **Plan Directory Presence:** 100% (every project has `/plan` with required files)

### User-Facing Metrics

- **Time Saved:** 3 hours → 3 minutes (60x improvement)
- **Cost Per Project:** $1-3 in API fees
- **Learning Curve:** < 10 minutes to first successful project

---

## Future Enhancements (Not in MVP)

Features to consider after initial release:

1. **GitHub Integration:** Create repo and push automatically
2. **Template Marketplace:** Community-contributed templates
3. **Revision System:** Iterate on existing projects with new features
4. **Alternative AI Providers:** Support GPT-4, Gemini as fallbacks
5. **Advanced Features:** Stripe setup, OAuth, Docker configs
6. **Team Features:** Shared templates, organizational defaults
7. **CI Integration:** Generate GitHub Actions for deployment
8. **Plan Evolution:** Tools to update `plan/` docs as project evolves

---

## Acceptance Criteria

This project is considered complete when:

### Functional Requirements
- [ ] All 5 questions capture user requirements accurately
- [ ] All 8 steps execute successfully for each template
- [ ] Generated projects run without additional configuration
- [ ] All generated tests pass
- [ ] All generated linters pass
- [ ] Git repository initialized with clean history
- [ ] Cost tracking accurate within 20%
- [ ] `/plan` directory created with all required documents

### Non-Functional Requirements
- [ ] Works on macOS, Linux, Windows
- [ ] Python 3.11+ required (no other dependencies)
- [ ] Installation via `pip install specinit`
- [ ] Total generation time < 5 minutes
- [ ] Clear error messages for all failure modes
- [ ] Comprehensive documentation

### Quality Requirements
- [ ] 80%+ test coverage (excluding UI)
- [ ] 50%+ UI test coverage
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] No critical security issues
- [ ] Documentation is complete and accurate
- [ ] Code follows PEP 8 (for Python) and project standards

---

## Appendix A: Tech Stack Compatibility Matrix

| Platform | Frontend | Backend | Database | Notes |
|----------|----------|---------|----------|-------|
| Web | React, Vue, Svelte | FastAPI, Express, Django | PostgreSQL, MongoDB | Most flexible |
| iOS + Android | React Native | FastAPI, Express | Supabase, Firebase | Cross-platform recommended |
| iOS only | SwiftUI | FastAPI | PostgreSQL | Native iOS |
| CLI | - | Python/Click | SQLite | Single-file database |
| API only | - | FastAPI, Express | PostgreSQL, MongoDB | Backend focused |

---

## Appendix B: Example Generated Project

**Input:**
- Platforms: Web
- User Story: As a freelancer, I want to track my time, so that I can bill clients accurately
- Features: Time tracking, Client management, Invoice generation
- Tech Stack: React, TypeScript, FastAPI, PostgreSQL
- Aesthetic: Professional, Minimalist

**Output Structure:**
```
time-tracker/
├── plan/
│   ├── product-spec.md
│   ├── progress-notes.md
│   └── audit-log.md
├── docs/
│   ├── README.md
│   ├── CONTRIBUTING.md
│   └── CLAUDE.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TimeEntry.tsx
│   │   │   ├── ClientList.tsx
│   │   │   └── InvoiceGenerator.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   └── Clients.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── tests/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── time_entries.py
│   │   │   ├── clients.py
│   │   │   └── invoices.py
│   │   ├── models/
│   │   └── main.py
│   └── tests/
├── .github/workflows/ci.yml
└── package.json

Appendix C: Plan Directory Specification
The /plan directory serves as the central repository for all project planning, specifications, and progress tracking. This directory should be created in Step 2 and populated throughout the generation process.
Required Files
plan/product-spec.md

Comprehensive product specification generated in Step 1
Contains: User requirements, features, architecture, data models, test strategy
Updated: Only in Step 1 (unless project regeneration/iteration added in future)

plan/progress-notes.md

Living document tracking development progress
Contains: Completion status of each phase, blockers, decisions made
Updated: After each step completion
Format:

markdown  # Progress Notes
  
  ## Step 1: Product Specification
  - Started: 2025-12-13 10:00:00
  - Completed: 2025-12-13 10:00:30
  - Notes: Generated comprehensive spec with 5 features
  
  ## Step 2: Project Structure
  - Started: 2025-12-13 10:00:31
  - Completed: 2025-12-13 10:00:45
  - Notes: Created 34 files across 8 directories
plan/audit-log.md

Self-audit results after each phase
Contains: Checklist validation, deviations from spec, quality metrics
Updated: After each step, especially Steps 5-8
Format:

markdown  # Audit Log
  
  ## Step 1 Audit
  ✓ Product spec includes all user requirements
  ✓ TDD strategy clearly defined
  ✓ Phases are well-structured
  
  ## Step 3 Audit
  ✓ README is comprehensive
  ✓ CONTRIBUTING includes testing workflow
  ⚠ CLAUDE.md could include more context about design decisions
Directory Permissions

All files should be read/write for owner
Version controlled (included in git)
Human-readable markdown format


Version History

v1.0.0 (December 13, 2025) - Initial specification for MVP release
v1.0.1 (December 13, 2025) - Updated to use /plan directory for all planning documents; added UI test coverage requirement of 50%


End of Specification
