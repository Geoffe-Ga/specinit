# Agent Context Templates

This directory contains language and framework-specific guidance for generating CLAUDE.md and AGENTS.md files in SpecInit-generated projects.

## Purpose

When SpecInit generates a new project, it needs to create agent context files that are:
1. **Project-specific** - Tailored to the generated project's structure
2. **Language-appropriate** - Following idioms and conventions of the chosen stack
3. **Framework-aware** - Including relevant patterns and gotchas

## How SpecInit Uses These Templates

1. SpecInit reads the base templates (`base-claude.md`, `base-agents.md`)
2. Augments with language-specific sections (e.g., `python.md`, `typescript.md`)
3. Augments with framework-specific sections (e.g., `fastapi.md`, `react.md`)
4. Inserts project-specific details (name, structure, features)
5. Writes final files to generated project

## Template Files

| File | Purpose |
|------|---------|
| `base-claude.md` | Core Claude-specific rules and patterns |
| `base-agents.md` | Provider-agnostic agent instructions |
| `python.md` | Python language conventions |
| `typescript.md` | TypeScript/JavaScript conventions |
| `react.md` | React framework patterns |
| `fastapi.md` | FastAPI framework patterns |
| `nextjs.md` | Next.js framework patterns |
| `cli.md` | CLI application patterns |

## Best Practices for Templates

### Must Include

1. **Critical Rules** - Non-negotiable constraints (testing, linting)
2. **Quick Start** - Exact commands to get running
3. **File Map** - Where to find things
4. **Common Tasks** - Step-by-step workflows
5. **Gotchas** - Framework/language-specific pitfalls

### Should Include

1. **Security Guidance** - Language-specific security patterns
2. **Testing Patterns** - Framework-appropriate test structure
3. **Error Handling** - Idiomatic error patterns
4. **Debugging Tips** - Common issues and solutions

### Must Avoid

1. **Vague guidance** - Be specific and actionable
2. **Duplicating docs** - Don't repeat what's in README
3. **Stale information** - Keep commands and versions current
4. **Assuming knowledge** - Explain project-specific decisions

## Placeholder Syntax

Templates use Jinja2 syntax for dynamic content:

```markdown
# {{ project_name }} - Agent Context

## Quick Start

```bash
{{ install_command }}
{{ test_command }}
```

## Project Structure

```
{{ project_structure }}
```
```

## Contributing

When adding new templates:
1. Follow the structure of existing templates
2. Include all "Must Include" sections
3. Test by generating a project and verifying the output
4. Update this README with the new template
