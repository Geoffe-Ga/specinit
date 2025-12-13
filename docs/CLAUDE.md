# CLAUDE.md - AI Context for SpecInit

This file provides context for AI assistants working on the SpecInit codebase.

## Project Overview

SpecInit is a CLI tool that generates complete project structures using Claude API. Users answer 5 questions through a web interface, and the tool orchestrates multiple Claude API calls to generate documentation, code, tests, and configuration files.

## Architecture

### Key Components

1. **CLI (`src/specinit/cli/`)**: Click-based commands (init, new, list, config)
2. **Server (`src/specinit/server/`)**: FastAPI server with WebSocket for progress updates
3. **Generator (`src/specinit/generator/`)**: 8-step generation orchestrator
4. **Storage (`src/specinit/storage/`)**: Config (YAML + keyring) and history (SQLite)
5. **Frontend (`frontend/`)**: React + Vite + Tailwind form wizard

### Data Flow

```
User → CLI → FastAPI Server → WebSocket
                    ↓
            Generator Orchestrator
                    ↓
            Claude API (8 steps)
                    ↓
            File Writer → Project Directory
```

## Important Files

| File | Purpose |
|------|---------|
| `src/specinit/cli/main.py` | CLI entry point |
| `src/specinit/generator/orchestrator.py` | Core generation logic |
| `src/specinit/generator/prompts.py` | Claude prompt templates |
| `src/specinit/generator/templates.py` | Built-in project templates |
| `src/specinit/storage/config.py` | Configuration management |
| `frontend/src/App.tsx` | Main React component |
| `frontend/src/components/ProjectForm.tsx` | 5-step form wizard |

## Key Decisions

### Why Click for CLI?
- Industry standard for Python CLIs
- Built-in help generation
- Easy command grouping

### Why FastAPI + WebSocket?
- WebSocket enables real-time progress updates
- FastAPI is fast and modern
- Easy to serve static frontend

### Why SQLite for History?
- Zero configuration
- Single file database
- Sufficient for local history

### Why Keyring for API Keys?
- Uses OS-native secure storage
- Better than plaintext in config files
- Works across platforms

## Common Tasks

### Adding a New Template

1. Edit `src/specinit/generator/templates.py`
2. Add template dict to `TEMPLATES`
3. Include: name, description, platforms, tech_stack, directory_structure

### Modifying Prompts

1. Edit `src/specinit/generator/prompts.py`
2. Update the relevant `build_*_prompt` method
3. Test with a sample generation

### Adding a CLI Command

1. Add function in `src/specinit/cli/main.py`
2. Decorate with `@cli.command()` or add to group
3. Add tests in `tests/unit/test_cli.py`

### Adding a Frontend Component

1. Create component in `frontend/src/components/`
2. Import in parent component
3. Use TypeScript for type safety

## Testing Notes

- Unit tests mock the Anthropic client
- Integration tests use temporary directories
- Frontend tests use React Testing Library
- Always test both success and error paths

## Known Gotchas

1. **API Key Storage**: Different behavior on macOS vs Linux vs Windows due to keyring backends
2. **WebSocket Connection**: Browser may cache failed connections; clear cache during development
3. **File Paths**: Always use `pathlib.Path` for cross-platform compatibility
4. **Cost Calculation**: Token counts are estimates; actual costs may vary by ~20%

## Performance Considerations

- Generation typically takes 2-5 minutes
- Most time is spent waiting for Claude API
- File operations are fast (< 1 second total)
- WebSocket keeps UI responsive

## Security Notes

- Never log API keys
- Config file has 600 permissions (user-only)
- No telemetry or external data transmission
- Validate all file paths to prevent directory traversal
