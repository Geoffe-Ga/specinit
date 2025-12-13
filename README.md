# SpecInit

AI-powered project initialization tool that transforms your ideas into working codebases in minutes.

## Overview

SpecInit is a local-first CLI tool that uses Claude to generate complete project structures with:
- Documentation (README, CONTRIBUTING, CLAUDE.md)
- Tests following TDD principles
- Linter and pre-commit configurations
- CI/CD pipelines
- Working demo code

**Core Value**: Reduce project initialization from 3 hours of manual setup to 3 minutes of guided configuration.

## Installation

```bash
pip install specinit
```

## Quick Start

1. **Initialize with your API key**:
   ```bash
   specinit init
   ```
   Enter your Anthropic API key when prompted.

2. **Create a new project**:
   ```bash
   specinit new
   ```
   This opens a web interface where you answer 5 questions about your project.

3. **Navigate to your project**:
   ```bash
   cd your-project-name
   npm install  # or pip install -e .
   npm run dev  # or python -m your_app
   ```

## Features

### 5-Question Configuration

1. **Target Platforms**: Web, iOS, Android, Desktop, CLI, API
2. **User Story**: Who, What, Why format
3. **Feature List**: Up to 10 features
4. **Tech Stack**: Frontend, Backend, Database, Tools
5. **UX Aesthetics**: Minimalist, Professional, Modern, etc.

### 8-Step Generation Process

| Step | Description | API Cost |
|------|-------------|----------|
| 1 | Product specification | ~$0.10-0.30 |
| 2 | Project structure | ~$0.05-0.10 |
| 3 | Documentation | ~$0.15-0.40 |
| 4 | Developer tooling | ~$0.10-0.25 |
| 5 | Validation | Free (local) |
| 6 | Dependencies | Free (local) |
| 7 | Git initialization | Free (local) |
| 8 | Demo code | ~$0.80-2.00 |

**Total cost per project**: $1.20-3.05

### Built-in Templates

- **react-fastapi**: React + FastAPI full-stack web app
- **react-native**: Cross-platform mobile app
- **nextjs**: Next.js web app with API routes
- **python-cli**: Python CLI tool with Click
- **fastapi-only**: API backend service

## CLI Commands

```bash
specinit init              # Set up API key
specinit new               # Start project generation
specinit list              # Show project history
specinit config show       # Display configuration
specinit config set KEY VALUE  # Update configuration
specinit config reset      # Reset to defaults
```

## Configuration

Config file location: `~/.specinit/config.yaml`

```yaml
api:
  model: claude-sonnet-4-5-20250929
  max_tokens: 100000

preferences:
  auto_open_editor: none  # or vscode, cursor
  auto_git_init: true
  cost_limit: 5.00
```

Environment variable: `SPECINIT_API_KEY`

## Generated Project Structure

```
your-project/
├── plan/
│   ├── product-spec.md    # Comprehensive specification
│   ├── progress-notes.md  # Development tracking
│   └── audit-log.md       # Quality audits
├── docs/
│   ├── README.md
│   ├── CONTRIBUTING.md
│   └── CLAUDE.md          # AI context for future work
├── src/                   # Application code
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD
├── .gitignore
├── .pre-commit-config.yaml
└── package.json           # or pyproject.toml
```

## Privacy

SpecInit is local-first:
- API keys stored encrypted using OS keyring
- No telemetry or data collection
- All data stays on your machine

## Requirements

- Python 3.11+
- Anthropic API key

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development setup and guidelines.
