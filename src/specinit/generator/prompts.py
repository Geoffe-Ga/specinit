"""Prompt templates for Claude API calls."""

from typing import Any


class PromptBuilder:
    """Builds prompts for each generation step."""

    BASE_SYSTEM = """You are an expert software architect specializing in project initialization and best practices.

Critical Guidelines:
1. **Test-Driven Development**: Write tests FIRST, then implementation
2. **No Shortcuts**: Never comment out failing tests or skip validation
3. **Documentation**: Update docs with every code change
4. **Best Practices**: Follow industry standards for chosen tech stack
5. **Conventional Commits**: Use clear, descriptive commit messages
6. **Completeness**: All code must be production-ready, not TODOs

Planning Directory:
All planning and specification documents should be saved in the /plan/ directory:
- product-spec.md - Comprehensive project specification
- progress-notes.md - Development progress tracking
- audit-log.md - Quality and compliance audits"""

    def _format_previous_outputs(self, context: dict[str, Any]) -> str:
        """Format previous outputs for inclusion in prompts.

        Args:
            context: Context dictionary that may contain previous_outputs

        Returns:
            Formatted string of previous outputs, or empty string if none
        """
        previous_outputs = context.get("previous_outputs", {})
        if not previous_outputs:
            return ""

        # Format outputs into a readable section
        formatted_files = [
            f"--- FILE: {file_path} ---\n{content}\n"
            for file_path, content in sorted(previous_outputs.items())
        ]

        files_text = "\n".join(formatted_files)
        return f"""
# Previous Step Outputs

The following files have been generated in previous steps. Use this content to inform your generation:

{files_text}
---
"""

    def build_product_spec_prompt(self, context: dict[str, Any]) -> str:
        """Build prompt for Step 1: Product Specification."""
        user_story = context["user_story"]
        features = context["features"]
        platforms = context["platforms"]
        tech_stack = context["tech_stack"]
        aesthetics = context["aesthetics"]
        additional_context = context.get("additional_context")

        additional_context_section = ""
        if additional_context:
            additional_context_section = f"""

## Additional Context
{additional_context}"""

        features_text = "\n".join(f"- {f}" for f in features)

        return f"""{self.BASE_SYSTEM}

# Context
The user wants to create a new software project with these requirements:

## Project Name
{context["project_name"]}

## Target Platforms
{", ".join(platforms)}

## User Story
As {user_story["role"]}, I want to {user_story["action"]}, so that {user_story["outcome"]}

## Features
{features_text}

## Tech Stack
- Frontend: {", ".join(tech_stack.get("frontend", ["N/A"]))}
- Backend: {", ".join(tech_stack.get("backend", ["N/A"]))}
- Database: {", ".join(tech_stack.get("database", ["N/A"]))}
- Tools: {", ".join(tech_stack.get("tools", ["N/A"]))}

## UX Aesthetics
{", ".join(aesthetics)}{additional_context_section}

# Your Task
Generate a comprehensive product specification document in Markdown format.

Include these sections:
1. Executive Summary
2. User Stories (expand on the primary, add 3-5 secondary)
3. Core Features (detailed breakdown of each feature)
4. Technical Architecture (system diagram, components, data flow)
5. Data Models (entities, relationships, schemas)
6. API Endpoints (if applicable)
7. UI/UX Specifications (screens, flows, component hierarchy)
8. Testing Strategy (unit, integration, e2e test plans)
9. Development Phases (break into 2-3 phases)
10. Success Criteria (measurable outcomes)

# Quality Checklist
Before finishing, verify:
- [ ] All user requirements are addressed
- [ ] Technical architecture is complete
- [ ] Data models cover all features
- [ ] Testing strategy is TDD-focused
- [ ] Phases are clearly defined with deliverables

Output ONLY the markdown content, no additional commentary."""

    def build_structure_prompt(self, context: dict[str, Any]) -> str:
        """Build prompt for Step 2: Project Structure."""
        template = context["template"]
        previous_outputs_section = self._format_previous_outputs(context)

        return f"""{self.BASE_SYSTEM}
{previous_outputs_section}
# Context
Create the project structure for: {context["project_name"]}

Template: {template["name"]}
Tech Stack:
- Frontend: {", ".join(context["tech_stack"].get("frontend", []))}
- Backend: {", ".join(context["tech_stack"].get("backend", []))}

# Your Task
Generate a bash script that creates all necessary directories and empty files for this project.

Required directories:
- plan/ (for product-spec.md, progress-notes.md, audit-log.md)
- docs/ (for README.md, CONTRIBUTING.md, CLAUDE.md)
- scripts/ (for lint.sh, test.sh, check.sh - consistency between local/CI)
- src/ or appropriate source directory
- tests/
- .github/workflows/

The script should:
1. Use mkdir -p for directories
2. Use touch for empty files
3. Include comments explaining the purpose of each section
4. Follow the template's directory structure

# Output Format
Output ONLY a bash script, starting with #!/bin/bash
No markdown code blocks, just the raw script."""

    def build_documentation_prompt(self, context: dict[str, Any]) -> str:
        """Build prompt for Step 3: Documentation (CONTRIBUTING and CLAUDE only).

        Note: README.md is generated later (after demo code) to reflect actual implementation.
        """
        user_story = context["user_story"]
        previous_outputs_section = self._format_previous_outputs(context)

        return f"""{self.BASE_SYSTEM}
{previous_outputs_section}
# Context
Project: {context["project_name"]}
User Story: As {user_story["role"]}, I want to {user_story["action"]}, so that {user_story["outcome"]}
Features: {", ".join(context["features"])}

# Your Task
Generate documentation files for development workflow.

NOTE: Do NOT generate README.md yet - it will be created later after the implementation is complete,
so it can accurately reflect the actual project code.

## Required Files

### docs/CONTRIBUTING.md
- Development setup instructions
- Code style guidelines
- Testing workflow
- Pull request process
- Issue templates

### docs/CLAUDE.md
CRITICAL: This file must include these exact sections at the top:

## Critical Rules

### No Shortcuts
**Never take shortcuts when fixing tests or checks:**
- Do not comment out or skip failing tests
- Do not relax linter rules or filters to make errors go away
- Do not change test assertions to match incorrect behavior
- All tests must test real functionality
- All checks must enforce valid requirements
- If a test fails, fix the underlying code, not the test (unless the test itself is wrong)

### Working Directory
**Always operate from the project root directory. Do not cd into subdirectories when running commands.** All paths in commands should be relative to the project root.

### Use Scripts for Consistency
**Always use the provided scripts in scripts/ for running tests and checks.** This ensures consistency between local development, pre-commit hooks, and CI.

After the Critical Rules section, also include:
- AI context for future development
- Key architectural decisions and rationale
- Known gotchas and edge cases
- Codebase tour (important files/directories)
- Common tasks and how to accomplish them

# Output Format
Output the files in this format:

--- FILE: docs/CONTRIBUTING.md ---
(content)

--- FILE: docs/CLAUDE.md ---
(content)

Output ONLY the file contents in this format, no additional commentary.
Do NOT include README.md - it will be generated later."""

    def build_tooling_prompt(self, context: dict[str, Any]) -> str:
        """Build prompt for Step 4: Developer Tooling."""
        tech_stack = context["tech_stack"]
        all_tech = (
            tech_stack.get("frontend", [])
            + tech_stack.get("backend", [])
            + tech_stack.get("tools", [])
        )
        previous_outputs_section = self._format_previous_outputs(context)

        return f"""{self.BASE_SYSTEM}
{previous_outputs_section}
# Context
Project: {context["project_name"]}
Tech Stack: {", ".join(all_tech)}

# Your Task
Generate STRICT, SECURITY-FOCUSED developer tooling configuration files.

## Philosophy
- Modern, battle-tested tools only
- Strict by default - catch bugs early
- Security checks enabled (bandit/security linting)
- Consistency between local dev, pre-commit, and CI
- Use scripts to run checks (not direct tool calls)

## Required Files

### scripts/lint.sh
```bash
#!/bin/bash
set -e
# Run all linting - matches CI exactly
```

### scripts/test.sh
```bash
#!/bin/bash
set -e
# Run all tests with coverage - matches CI exactly
```

### scripts/check.sh
```bash
#!/bin/bash
set -e
./scripts/lint.sh
./scripts/test.sh
```

### For Python projects - pyproject.toml must include:
```toml
[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "S",      # flake8-bandit (SECURITY)
    "PTH",    # flake8-use-pathlib
    "RUF",    # Ruff-specific rules
    "PERF",   # Perflint (performance)
    "PL",     # Pylint
]
```

### For JavaScript/TypeScript projects:
- ESLint with security plugin (eslint-plugin-security)
- TypeScript strict mode enabled
- Prettier for formatting
- CRITICAL: Use React 18 compatible versions in package.json:
  - react: 18.3.1 (latest React 18.x, compatible with Expo/RN)
  - react-dom: 18.3.1 (if using React for web)
  - @types/react: ^18.3.0 (for TypeScript projects)
  - @types/react-dom: ^18.3.0 (for TypeScript web projects)
  - react-test-renderer: 18.3.1 (for testing with React Native/Expo)
  - Avoid React 19+ as Expo/React Native don't fully support it yet

### For Expo/React Native projects:
- CRITICAL: Use Expo SDK 52 compatible versions:
  - expo: ~52.0.0
  - react-native: 0.76.5 (exact version required by Expo 52)
  - react: 18.3.1 (required by Expo 52)
  - expo-router: ~4.0.0 (if using file-based routing)
  - Use `npx expo install <package>` to ensure version compatibility
  - Avoid manually specifying versions that conflict with Expo SDK

### For Expo projects with web support:
- CRITICAL: Include web-specific dependencies when "web" is a target platform:
  - react-dom: 18.3.1 (required for web rendering)
  - react-native-web: ~0.19.13 (bridges React Native to web, compatible with SDK 52)
    # Source: https://expo.dev/changelog/2024-11-12-sdk-52
    # Verified via: npx expo install --check confirms compatible versions
  - @expo/metro-runtime: ~4.0.0 (Expo web runtime)
- Configure app.json to include "web" in platforms array
- Ensure metro.config.js supports web platform
- Note: Web support requires additional setup compared to native platforms

### .pre-commit-config.yaml
- Use LOCAL hooks (not external repos) to ensure same versions as CI
- Run via `python -m <tool>` for consistency

### .github/workflows/ci.yml
- Run ./scripts/lint.sh and ./scripts/test.sh
- Test on multiple Python/Node versions
- Fail fast on any error

## Key Principles
1. Pre-commit and CI MUST run identical checks
2. All security linting enabled (S rules for Python, security plugin for JS)
3. Scripts wrap all commands for consistency
4. Strict type checking where applicable

# Output Format
Output the files in this format:

--- FILE: scripts/lint.sh ---
(content)

--- FILE: scripts/test.sh ---
(content)

--- FILE: pyproject.toml ---
(content)

(etc.)

Output ONLY the file contents in this format, no additional commentary."""

    def build_demo_code_prompt(self, context: dict[str, Any], spec_content: str) -> str:
        """Build prompt for Step 8: Demo Code."""
        additional_context = context.get("additional_context")
        previous_outputs_section = self._format_previous_outputs(context)

        additional_context_section = ""
        if additional_context:
            additional_context_section = f"""

## Additional Context
{additional_context}"""

        return f"""{self.BASE_SYSTEM}
{previous_outputs_section}
# Context
Project: {context["project_name"]}
Features: {", ".join(context["features"])}

## Product Specification
{spec_content[:8000]}  # Truncate if too long{additional_context_section}

# Your Task
Generate working demo code that demonstrates the core features.

## Requirements
1. **TDD**: Write tests FIRST, then implementation
2. **Minimal but Complete**: Show key features working, not every edge case
3. **Runnable**: Code must work without modification
4. **Well-Documented**: Include docstrings and comments

## Include
- Basic routing/navigation
- Example components/modules for each feature
- API endpoints (if backend)
- Database models (if applicable)
- Unit tests for core logic
- Integration test for main flow

# Output Format
Output the files in this format:

--- FILE: src/main.py ---
(content)

--- FILE: tests/test_main.py ---
(content)

(etc.)

Output ONLY the file contents in this format, no additional commentary.
Each file should be complete and functional."""

    def build_readme_prompt(
        self, context: dict[str, Any], spec_content: str, project_files: list[str]
    ) -> str:
        """Build prompt for README generation (after demo code is complete).

        This generates a README that reflects the actual implementation,
        not just a generic template.
        """
        user_story = context["user_story"]
        additional_context = context.get("additional_context")

        additional_context_section = ""
        if additional_context:
            additional_context_section = f"""

## Additional Context
{additional_context}"""

        files_summary = "\n".join(f"- {f}" for f in project_files[:50])  # Limit to first 50

        return f"""{self.BASE_SYSTEM}

# Context
Project: {context["project_name"]}
User Story: As {user_story["role"]}, I want to {user_story["action"]}, so that {user_story["outcome"]}
Features: {", ".join(context["features"])}
Platforms: {", ".join(context["platforms"])}

## Tech Stack
- Frontend: {", ".join(context["tech_stack"].get("frontend", ["N/A"]))}
- Backend: {", ".join(context["tech_stack"].get("backend", ["N/A"]))}
- Database: {", ".join(context["tech_stack"].get("database", ["N/A"]))}
- Tools: {", ".join(context["tech_stack"].get("tools", ["N/A"]))}{additional_context_section}

## Product Specification (Excerpt)
{spec_content[:4000]}  # Truncate to stay within token limits

## Generated Project Structure
{files_summary}

# Your Task
Generate a comprehensive README.md that accurately documents THIS SPECIFIC PROJECT.

CRITICAL: This README must reflect the ACTUAL implementation, not a generic template.
You must base the documentation on:
1. The user story and features provided
2. The product specification above
3. The actual project structure and files listed
4. The tech stack selected

## Required Sections

### Project Title and Description
- Use the project name: {context["project_name"]}
- Write a compelling description based on the user story
- Explain the value proposition clearly

### Features
- List the ACTUAL features implemented (from the features list)
- Provide brief descriptions of what each feature does
- Include screenshots placeholders if relevant for the platform

### Tech Stack
- Document the actual technologies used
- Explain why they were chosen (based on requirements)
- Include version information where relevant

### Getting Started

#### Prerequisites
- List required software/tools for THIS specific tech stack
- Include version requirements

#### Installation
- Provide exact commands for THIS project structure
- Include platform-specific instructions if needed (iOS/Android/Web)

#### Configuration
- Document any required environment variables
- Explain configuration files that were generated

#### Running the Application
- Provide commands to run in development mode
- Include commands for different platforms if applicable
- Document how to access the application (URL, ports, etc.)

### Project Structure
- Explain the directory layout that was ACTUALLY created
- Describe the purpose of key directories and files
- Make it specific to THIS project, not generic

### Development

#### Running Tests
- Show how to run the test suite that was generated
- Explain the testing approach used

#### Linting and Formatting
- Document the linters/formatters configured
- Show commands to run them

#### Pre-commit Hooks
- Explain that pre-commit hooks are configured
- Show how to install and use them

### API Documentation (if applicable)
- If this is a backend/API project, document the endpoints
- Include example requests/responses
- Reference the OpenAPI/Swagger docs if generated

### Deployment (if applicable)
- Provide deployment instructions for the chosen platform
- Include CI/CD information if configured

### Contributing
- Reference the CONTRIBUTING.md file
- Encourage contributions

### License
- Specify the license (MIT recommended)

# Output Format
Output ONLY the README.md content in markdown format.
Start with the project title as an H1 heading.
Do NOT include "--- FILE: ---" markers.
Do NOT add extra commentary."""
