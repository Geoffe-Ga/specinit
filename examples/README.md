# SpecInit Examples

This directory contains examples demonstrating SpecInit functionality.

## Demo Script

Run the demo to see SpecInit's core logic in action (no API calls required):

```bash
# From project root
python examples/demo.py
```

This demonstrates:
- **Template Selection**: How SpecInit picks the right template based on platforms and tech stack
- **Cost Estimation**: Token tracking and pricing for Claude API calls
- **Prompt Building**: How prompts are constructed for each generation step

## Interactive Usage

To use SpecInit interactively:

```bash
# Initialize with your Anthropic API key
specinit init

# Start project generation (opens web UI at http://localhost:8765)
specinit new

# View generation history
specinit list

# Manage configuration
specinit config show
specinit config set cost_limit 10.00
```

## Configuration Questions

When you run `specinit new`, you'll answer 6 questions:

1. **Target Platforms**: Web, iOS, Android, Desktop, CLI, API
2. **User Story**: Who, What, Why format
3. **Feature List**: Up to 10 features
4. **Tech Stack**: Frontend, Backend, Database, Tools
5. **UX Aesthetics**: Minimalist, Professional, Modern, etc.
6. **GitHub Mode**: Local-only or issue-driven development

## Generated Project Structure

```
your-project/
├── plan/
│   ├── product-spec.md      # Comprehensive specification
│   ├── progress-notes.md    # Development tracking
│   └── audit-log.md         # Quality audits
├── docs/
│   ├── README.md            # User documentation
│   ├── CONTRIBUTING.md      # Dev guidelines
│   └── CLAUDE.md            # AI context
├── src/                     # Application code
├── tests/                   # Test suite
├── .github/workflows/       # CI/CD
├── .pre-commit-config.yaml  # Pre-commit hooks
└── pyproject.toml           # or package.json
```

## Cost Estimates

| Mode | Estimated Cost |
|------|---------------|
| Local Mode | $1.20 - $3.05 |
| GitHub Mode | $2.00 - $4.00 |
| GitHub + YOLO | $3.00 - $6.00 |
