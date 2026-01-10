"""Launcher module for starting the SpecInit server.

This module provides a facade for starting the server without creating
a static import dependency from CLI to Server. This enables the import-linter
independence contract between CLI and Server (Issue #72).

The lazy import pattern ensures that specinit.server.app is only imported
at runtime when start_server is actually called, not at module load time.
"""

from pathlib import Path


def start_server(port: int = 8765, output_dir: Path | None = None) -> None:
    """Start the SpecInit web server.

    This function delegates to specinit.server.app.start_server using
    a lazy import to avoid creating a static dependency from CLI to Server.

    Args:
        port: Port number for the server (default: 8765)
        output_dir: Directory for generated project output (default: cwd)
    """
    # Lazy import to break static dependency (intentional)
    from specinit.server.app import start_server as _start_server

    _start_server(port=port, output_dir=output_dir)
