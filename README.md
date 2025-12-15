<p align="center">
  <img src="docs/assets/logo.png" alt="SpecInit Logo" width="120" />
</p>

<h1 align="center">SpecInit</h1>

<p align="center">
  <strong>Transform project ideas into working codebases in minutes, not hours.</strong>
</p>

<p align="center">
  <a href="https://github.com/Geoffe-Ga/specinit/actions/workflows/ci.yml">
    <img src="https://github.com/Geoffe-Ga/specinit/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="https://codecov.io/gh/Geoffe-Ga/specinit">
    <img src="https://codecov.io/gh/Geoffe-Ga/specinit/branch/main/graph/badge.svg" alt="Coverage" />
  </a>
  <a href="https://pypi.org/project/specinit/">
    <img src="https://img.shields.io/pypi/v/specinit.svg" alt="PyPI Version" />
  </a>
  <a href="https://pypi.org/project/specinit/">
    <img src="https://img.shields.io/pypi/pyversions/specinit.svg" alt="Python Versions" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  </a>
</p>

---

## The Problem

Every new project starts the same way: hours of boilerplate setup. README templates. CI configuration. Linter rules. Test scaffolding. Directory structures. By the time you write your first feature, you've already spent half a day on ceremony.

**SpecInit solves this.**

Answer 5 questions about your project. Get a complete, production-ready codebase with documentation, tests, CI/CD, and working demo code in under 5 minutes.

---

## Demo

<p align="center">
  <img src="docs/assets/demo.gif" alt="SpecInit Demo" width="600" />
</p>

```bash
$ specinit new

? Target platforms: Web
? User story: As a developer, I want to track my time so I can bill clients accurately
? Core features: Timer, Project management, Reports, Export to CSV
? Tech stack: React + FastAPI
? Visual style: Minimalist

Generating project... ━━━━━━━━━━━━━━━━━━━━ 100%

✓ Created: timetracker/
  ├── Full product specification
  ├── React frontend with components
  ├── FastAPI backend with routes
  ├── 47 unit tests (all passing)
  ├── CI/CD pipeline
  └── Ready to run: cd timetracker && npm install && npm run dev
```

---

## Quick Start

```bash
# Install SpecInit
pip install specinit

# Initialize with your Anthropic API key
specinit init

# Generate your first project
specinit new
```

That's it. A browser window opens with a 5-question wizard. Answer the questions, watch the generation progress in real-time, and your project is ready.

---

## What You Get

Every generated project includes:

| Component | Description |
|-----------|-------------|
| **Product Spec** | Detailed specification from your answers (`plan/product-spec.md`) |
| **Source Code** | Working application matching your tech stack |
| **Tests** | Unit tests with 80%+ coverage, following TDD principles |
| **Documentation** | README, CONTRIBUTING, and CLAUDE.md for AI-assisted development |
| **CI/CD** | GitHub Actions workflow for testing and deployment |
| **Dev Tools** | Pre-commit hooks, linter config, type checking |
| **Git Ready** | Initialized repo with proper .gitignore |

### Generated Project Structure

```
your-project/
├── plan/
│   ├── product-spec.md      # What we're building and why
│   ├── progress-notes.md    # Development tracking
│   └── audit-log.md         # Quality checkpoints
├── src/                     # Application code
├── tests/                   # Test suite
├── docs/
│   ├── README.md            # Project documentation
│   ├── CONTRIBUTING.md      # Contribution guidelines
│   └── CLAUDE.md            # AI assistant context
├── .github/workflows/       # CI/CD pipelines
├── .pre-commit-config.yaml  # Code quality hooks
└── [package.json|pyproject.toml]
```

---

## Built-in Templates

| Template | Stack | Best For |
|----------|-------|----------|
| `react-fastapi` | React + FastAPI + SQLite | Full-stack web applications |
| `nextjs` | Next.js + API Routes | Server-rendered React apps |
| `react-native` | React Native + Expo | Cross-platform mobile apps |
| `python-cli` | Python + Click | Command-line tools |
| `fastapi-only` | FastAPI + Pydantic | API backend services |

---

## How It Works

SpecInit orchestrates 8 generation steps, each using Claude to produce specific outputs:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your Answers  │────▶│  Claude API     │────▶│  Your Project   │
│   (5 questions) │     │  (8 steps)      │     │  (ready to run) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

| Step | What It Does | Cost |
|------|--------------|------|
| 1. Product Spec | Expands your answers into detailed requirements | ~$0.10-0.30 |
| 2. Structure | Designs directory layout and file organization | ~$0.05-0.10 |
| 3. Documentation | Generates README, CONTRIBUTING, CLAUDE.md | ~$0.15-0.40 |
| 4. Dev Tooling | Creates linter, pre-commit, CI/CD configs | ~$0.10-0.25 |
| 5. Validation | Verifies generated files locally | Free |
| 6. Dependencies | Resolves and validates package dependencies | Free |
| 7. Git Init | Initializes repository with proper .gitignore | Free |
| 8. Demo Code | Generates working application code with tests | ~$0.80-2.00 |

**Total cost per project: $1.20-3.05** (varies by project complexity)

---

## Architecture

> For AI assistants: This section explains the codebase structure and design decisions.

### Components

```
specinit/
├── src/specinit/
│   ├── cli/                 # Click CLI commands
│   │   └── main.py          # Entry point: init, new, list, config
│   ├── server/              # FastAPI web server
│   │   ├── app.py           # API routes and WebSocket
│   │   └── static/          # Built frontend assets
│   ├── generator/           # Core generation logic
│   │   ├── orchestrator.py  # 8-step generation coordinator
│   │   ├── prompts.py       # Claude prompt templates
│   │   └── templates.py     # Built-in project templates
│   └── storage/             # Data persistence
│       ├── config.py        # YAML config + keyring for API keys
│       └── history.py       # SQLite project history
├── frontend/                # React + Vite + Tailwind
│   └── src/
│       ├── App.tsx          # Main application
│       └── components/      # Form wizard components
└── tests/
    ├── unit/                # Isolated unit tests
    └── integration/         # End-to-end generation tests
```

### Key Design Decisions

| Decision | Why |
|----------|-----|
| **Click for CLI** | Industry standard, auto-generated help, command grouping |
| **FastAPI + WebSocket** | Real-time progress updates during generation |
| **SQLite for history** | Zero-config, single-file, perfect for local storage |
| **Keyring for secrets** | OS-native secure storage (macOS Keychain, Windows Credential Locker) |
| **Local-first** | No server dependency, works offline after API calls |

### Data Flow

```
User Input → CLI → FastAPI Server → WebSocket (progress)
                        ↓
                Generator Orchestrator
                        ↓
                Claude API (8 steps)
                        ↓
                File Writer → Project Directory
```

---

## CLI Reference

```bash
# Setup
specinit init                  # Configure API key (stored securely in OS keyring)

# Project Generation
specinit new                   # Start interactive project generation
specinit new --no-browser      # API-only mode (for custom frontends)

# History
specinit list                  # Show previously generated projects
specinit list --json           # Machine-readable output

# Configuration
specinit config show           # Display current settings
specinit config set KEY VALUE  # Update a setting
specinit config reset          # Reset to defaults
```

---

## Configuration

**Config location:** `~/.specinit/config.yaml`

```yaml
api:
  model: claude-sonnet-4-5-20250929    # Claude model to use
  max_tokens: 100000                   # Maximum tokens per request

preferences:
  auto_open_editor: none               # Options: none, vscode, cursor
  auto_git_init: true                  # Initialize git repo automatically
  cost_limit: 5.00                     # Abort if estimated cost exceeds this
```

**Environment variables:**
- `SPECINIT_API_KEY` - Anthropic API key (overrides keyring)
- `SPECINIT_CONFIG_DIR` - Custom config directory

---

## Privacy & Security

SpecInit is designed with privacy as a core principle:

- **Local-first architecture** - All processing happens on your machine
- **Secure credential storage** - API keys stored in OS keyring (macOS Keychain, Windows Credential Locker, Linux Secret Service)
- **No telemetry** - Zero data collection, no analytics, no phone-home
- **No cloud dependency** - Works offline after initial API calls
- **Open source** - Full transparency into what the code does

Your project ideas and generated code never leave your machine (except for Claude API calls to generate content).

---

## Requirements

- **Python 3.11+**
- **Anthropic API key** ([Get one here](https://console.anthropic.com/))

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Development setup
- Testing guidelines
- Code style requirements
- Pull request process

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with Claude by developers who were tired of writing boilerplate.</sub>
</p>
