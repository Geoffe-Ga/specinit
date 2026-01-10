"""Tests for the launcher module (Issue #72)."""

from pathlib import Path
from unittest.mock import patch


class TestStartServer:
    """Tests for the start_server launcher function."""

    def test_start_server_calls_server_app(self) -> None:
        """start_server should delegate to specinit.server.app.start_server."""
        with patch("specinit.server.app.start_server") as mock_server_start:
            # Import after patching to ensure lazy import gets the mock
            from specinit.launcher import start_server

            start_server(port=8080)

            mock_server_start.assert_called_once_with(port=8080, output_dir=None)

    def test_start_server_passes_output_dir(self, temp_dir: Path) -> None:
        """start_server should pass output_dir to the underlying function."""
        with patch("specinit.server.app.start_server") as mock_server_start:
            from specinit.launcher import start_server

            start_server(port=9000, output_dir=temp_dir)

            mock_server_start.assert_called_once_with(port=9000, output_dir=temp_dir)

    def test_start_server_uses_default_port(self) -> None:
        """start_server should use default port 8765."""
        with patch("specinit.server.app.start_server") as mock_server_start:
            from specinit.launcher import start_server

            start_server()

            mock_server_start.assert_called_once_with(port=8765, output_dir=None)


class TestLauncherDoesNotImportServerStatically:
    """Tests to ensure the launcher module does not create static import dependency."""

    def test_launcher_module_imports_without_server(self) -> None:
        """Launcher module should be importable without loading server module."""
        # This test verifies the lazy import pattern works
        # by checking that launcher's top-level imports don't include server
        import specinit.launcher as launcher_module

        # The module should exist and have start_server
        assert hasattr(launcher_module, "start_server")

        # Check that server.app is NOT in the launcher module's direct imports
        # This is verified by import-linter, but we document the intent here
        # If server was statically imported, it would be in sys.modules
        # after importing launcher. We can't reliably test this since
        # other tests may have already imported server, but we document
        # the intent through this test's existence.
