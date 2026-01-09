"""Main CLI entry point for SpecInit."""

import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from specinit import __version__
from specinit.launcher import start_server
from specinit.storage.config import ConfigManager
from specinit.storage.history import HistoryManager

console = Console()


def validate_port(_ctx: click.Context, _param: click.Parameter, value: int) -> int:
    """Validate port is in valid range (1024-65535).

    Issue #12 Fix: Validate port number to avoid confusing runtime errors.
    Rejects privileged ports (< 1024) that require elevated permissions
    and invalid ports (> 65535).
    """
    if value < 1024:
        raise click.BadParameter(
            f"Port {value} requires elevated permissions. Use a port between 1024 and 65535."
        )
    if value > 65535:
        raise click.BadParameter(f"Port {value} is invalid. Use a port between 1024 and 65535.")
    return value


@click.group()
@click.version_option(version=__version__, prog_name="specinit")
def cli() -> None:
    """SpecInit - AI-powered project initialization tool.

    Transform your project ideas into working codebases in minutes.
    """
    pass


@cli.command()
@click.option(
    "--api-key",
    prompt="Enter your Anthropic API key",
    hide_input=True,
    help="Your Anthropic API key for Claude access.",
)
def init(api_key: str) -> None:
    """Initialize SpecInit with your API key.

    This sets up the configuration needed to generate projects.
    """
    config = ConfigManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Validating API key...", total=None)

        # Validate the API key format
        if not api_key.startswith("sk-ant-"):
            console.print("[red]Error:[/red] Invalid API key format.")
            console.print("API keys should start with 'sk-ant-'")
            console.print("\nGet an API key: https://console.anthropic.com/")
            raise SystemExit(1)

        # Store the API key
        config.set_api_key(api_key)

    console.print("[green]Success![/green] SpecInit is ready to use.")
    console.print("\nNext steps:")
    console.print("  specinit new           Start creating a new project")
    console.print("  specinit config show   View your configuration")


@cli.command()
@click.option(
    "--port",
    default=8765,
    callback=validate_port,
    help="Port for the local web server (1024-65535).",
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Don't automatically open the browser.",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for the generated project.",
)
def new(port: int, no_browser: bool, output_dir: Path | None) -> None:
    """Start a new project generation.

    Opens a web interface to configure your project, then generates
    a complete codebase with documentation, tests, and configuration.
    """
    config = ConfigManager()

    # Check for API key
    if not config.get_api_key():
        console.print("[red]Error:[/red] No API key configured.")
        console.print("\nRun 'specinit init' to set up your API key first.")
        raise SystemExit(1)

    # Set output directory
    if output_dir is None:
        output_dir = Path.cwd()

    console.print("[bold]SpecInit[/bold] - Project Generator")
    console.print(f"Starting web server on http://localhost:{port}")

    if not no_browser:
        webbrowser.open(f"http://localhost:{port}")

    # Start the server (this will block until generation is complete)
    start_server(port=port, output_dir=output_dir)


@cli.command()
@click.option(
    "--limit",
    "-n",
    default=10,
    help="Number of projects to show.",
)
def list(limit: int) -> None:
    """List previously generated projects.

    Shows your project history with generation dates and costs.
    """
    history = HistoryManager()
    projects = history.get_recent(limit=limit)

    if not projects:
        console.print("No projects generated yet.")
        console.print("\nRun 'specinit new' to create your first project!")
        return

    console.print("[bold]Recent Projects[/bold]\n")

    for project in projects:
        console.print(f"[cyan]{project['name']}[/cyan]")
        console.print(f"  Created: {project['created_at']}")
        console.print(f"  Path: {project['path']}")
        console.print(f"  Cost: ${project['cost']:.2f}")
        console.print()


@cli.group()
def config() -> None:
    """Manage SpecInit configuration."""
    pass


@config.command("show")
def config_show() -> None:
    """Display current configuration."""
    cfg = ConfigManager()
    settings = cfg.get_all()

    console.print("[bold]Current Configuration[/bold]\n")

    # API key (masked)
    api_key = settings.get("api_key", "")
    if api_key:
        masked = api_key[:10] + "..." + api_key[-4:]
        console.print(f"API Key: {masked}")
    else:
        console.print("API Key: [red]Not set[/red]")

    # Other settings
    console.print(f"Model: {settings.get('model', 'claude-sonnet-4-5-20250929')}")
    console.print(f"Cost Limit: ${settings.get('cost_limit', 5.0):.2f}")
    console.print(f"Auto Open Editor: {settings.get('auto_open_editor', 'none')}")
    console.print(f"Auto Git Init: {settings.get('auto_git_init', True)}")

    # Usage stats
    console.print("\n[bold]Usage Statistics[/bold]")
    console.print(f"Projects Created: {settings.get('projects_created', 0)}")
    console.print(f"Total Cost: ${settings.get('total_cost', 0.0):.2f}")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value.

    Available keys: api_key, model, cost_limit, auto_open_editor, auto_git_init
    """
    cfg = ConfigManager()

    valid_keys = ["api_key", "model", "cost_limit", "auto_open_editor", "auto_git_init"]

    if key not in valid_keys:
        console.print(f"[red]Error:[/red] Unknown configuration key '{key}'")
        console.print(f"\nValid keys: {', '.join(valid_keys)}")
        raise SystemExit(1)

    # Type conversion
    config_value: str | float | bool = value
    if key == "cost_limit":
        try:
            config_value = float(value)
        except ValueError as err:
            console.print("[red]Error:[/red] cost_limit must be a number")
            raise SystemExit(1) from err
    elif key == "auto_git_init":
        config_value = value.lower() in ("true", "1", "yes")

    cfg.set(key, config_value)
    console.print(f"[green]Success![/green] Set {key}")


@config.command("reset")
@click.confirmation_option(prompt="Are you sure you want to reset all settings?")
def config_reset() -> None:
    """Reset configuration to defaults."""
    cfg = ConfigManager()
    cfg.reset()
    console.print("[green]Configuration reset to defaults.[/green]")


if __name__ == "__main__":
    cli()
