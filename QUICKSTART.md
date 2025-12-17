# SpecInit Quickstart Guide

Get from zero to generating projects in under 5 minutes.

## Prerequisites

- Python 3.11 or higher
- An [Anthropic API key](https://console.anthropic.com/)
- Node.js 18+ (for frontend development only)

## Installation

> **Note**: SpecInit is not yet published to PyPI. Install directly from GitHub using one of the methods below.

### Option 1: Install with pipx from GitHub (Recommended)

[pipx](https://pipx.pypa.io/) installs Python CLI tools in isolated environments, avoiding system Python conflicts.

```bash
# Install pipx if you don't have it
brew install pipx  # macOS
# or: sudo apt install pipx  # Ubuntu/Debian

pipx ensurepath  # Add pipx to your PATH (restart terminal after)

# Install SpecInit from GitHub
pipx install git+https://github.com/Geoffe-Ga/specinit.git
```

### Option 2: Install in a Virtual Environment

If you see `externally-managed-environment` errors or prefer manual setup:

```bash
# Create and activate a virtual environment
python3 -m venv ~/.specinit-venv
source ~/.specinit-venv/bin/activate  # Windows: ~/.specinit-venv\Scripts\activate

# Install SpecInit from GitHub
pip install git+https://github.com/Geoffe-Ga/specinit.git

# Verify installation
specinit --help
```

To use `specinit` without activating the venv each time:
```bash
# Add alias to your shell profile
echo 'alias specinit="~/.specinit-venv/bin/specinit"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc
```

### Option 3: Install from Cloned Source (For Development)

```bash
git clone https://github.com/Geoffe-Ga/specinit.git
cd specinit

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in editable/development mode
pip install -e ".[dev]"

# Verify installation
specinit --help
```

> **Note for macOS/Homebrew users**: Modern Python installations (PEP 668) prevent installing packages system-wide to protect your system. Always use pipx or a virtual environment.

## Setup

Initialize SpecInit with your Anthropic API key:

```bash
specinit init
```

You'll be prompted to enter your API key. It's stored securely in your system's keyring (never in plain text files).

## Generate Your First Project

```bash
specinit new
```

This opens a browser-based wizard where you answer 5 questions:

1. **Platforms** - Where will your app run? (Web, iOS, Android, CLI, API)
2. **User Story** - Who is the user and what do they want to accomplish?
3. **Features** - What are the core features?
4. **Tech Stack** - What technologies do you want to use?
5. **Aesthetics** - What visual style? (Minimalist, Playful, Corporate, etc.)

After answering, SpecInit generates a complete project with:
- Working source code
- Unit tests
- Documentation (README, CONTRIBUTING)
- CI/CD configuration
- Pre-commit hooks
- Git repository

## Available Commands

```bash
specinit init              # Set up API key
specinit new               # Generate a new project
specinit new --port 3000   # Use custom port for wizard
specinit list              # View generation history
specinit config show       # View current configuration
specinit config set KEY VALUE  # Update configuration
specinit status            # Check API key and GitHub token status
```

## Configuration Options

| Key | Description | Default |
|-----|-------------|---------|
| `cost_limit` | Maximum spend per project ($) | 5.00 |
| `model` | Claude model to use | claude-sonnet-4-5-20250929 |
| `auto_git_init` | Initialize git repo automatically | true |
| `auto_open_editor` | Open editor after generation | none |

Set options with:
```bash
specinit config set cost_limit 10.00
specinit config set auto_open_editor vscode
```

## GitHub Integration (Optional)

Connect GitHub to automatically create repositories and issues:

```bash
specinit github login
```

This stores your GitHub token securely in your system keyring.

## Cost Transparency

SpecInit shows you:
- **Estimated cost** before generation starts
- **Real-time cost tracking** during generation
- **Final cost** when complete

Typical project generation costs $0.50 - $2.00 depending on complexity.

## Example: Creating a Task Manager

```bash
$ specinit new

# In the browser wizard:
# Platforms: Web
# User Story: As a busy professional, I want to manage my tasks so I can stay organized
# Features: Task lists, Due dates, Priority levels, Search, Tags
# Tech Stack: React, FastAPI, PostgreSQL
# Aesthetics: Minimalist

# SpecInit generates:
# - React frontend with components for tasks, lists, search
# - FastAPI backend with CRUD endpoints
# - PostgreSQL schema with migrations
# - 50+ unit tests
# - Docker configuration
# - GitHub Actions CI/CD
```

## Project Templates

SpecInit includes 5 built-in templates:

| Template | Best For |
|----------|----------|
| `react-fastapi` | Full-stack web apps |
| `nextjs` | Server-rendered React apps |
| `react-native` | Cross-platform mobile apps |
| `python-cli` | Command-line tools |
| `fastapi-only` | API backends |

The template is auto-selected based on your answers, or you can specify one.

## Troubleshooting

### "externally-managed-environment" error

This error occurs on macOS (Homebrew), Ubuntu 23.04+, and other systems using PEP 668:

```
error: externally-managed-environment
× This environment is externally managed
```

**Solution**: Use pipx or a virtual environment:

```bash
# Option A: Use pipx (recommended)
brew install pipx && pipx install git+https://github.com/Geoffe-Ga/specinit.git

# Option B: Use a virtual environment
python3 -m venv ~/.specinit-venv
~/.specinit-venv/bin/pip install git+https://github.com/Geoffe-Ga/specinit.git
~/.specinit-venv/bin/specinit --help
```

### "No API key configured"
Run `specinit init` and enter your Anthropic API key.

### "Invalid API key format"
API keys must start with `sk-ant-`. Get one from [console.anthropic.com](https://console.anthropic.com/).

### Port already in use
Use a different port: `specinit new --port 9000`

### Generation fails midway
- Check your internet connection
- Verify your API key is valid
- Check you haven't exceeded your Anthropic rate limits

## Development Setup

For contributing to SpecInit:

```bash
# Clone and install dev dependencies
git clone https://github.com/Geoffe-Ga/specinit.git
cd specinit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
./scripts/test.sh

# Run linting
./scripts/lint.sh
```

## Getting Help

- **Documentation**: See [README.md](README.md) for full documentation
- **Issues**: Report bugs at [GitHub Issues](https://github.com/Geoffe-Ga/specinit/issues)
- **AI Instructions**: See [CLAUDE.md](CLAUDE.md) for AI-assisted development context

## Next Steps

1. Generate your first project with `specinit new`
2. Explore the generated code and tests
3. Customize the project to your needs
4. Connect GitHub for automated repo creation
5. Share feedback and contribute improvements!
