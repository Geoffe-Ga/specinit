"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from specinit.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI runner."""
    return CliRunner()


class TestInitCommand:
    """Tests for the init command."""

    def test_init_with_valid_api_key(self, runner: CliRunner, _mock_home: Path) -> None:
        """Valid API key should be stored successfully."""
        with patch("specinit.cli.main.ConfigManager") as mock_config:
            mock_instance = MagicMock()
            mock_config.return_value = mock_instance

            result = runner.invoke(cli, ["init"], input="sk-ant-test-key-12345\n")

            assert result.exit_code == 0
            assert "Success" in result.output
            mock_instance.set_api_key.assert_called_once_with("sk-ant-test-key-12345")

    def test_init_with_invalid_api_key(self, runner: CliRunner, _mock_home: Path) -> None:
        """Invalid API key format should show error."""
        result = runner.invoke(cli, ["init"], input="invalid-key\n")

        assert result.exit_code == 1
        assert "Invalid API key format" in result.output


class TestNewCommand:
    """Tests for the new command."""

    def test_new_without_api_key_fails(self, runner: CliRunner, _mock_home: Path) -> None:
        """New command should fail without API key."""
        with patch("specinit.cli.main.ConfigManager") as mock_config:
            mock_instance = MagicMock()
            mock_instance.get_api_key.return_value = None
            mock_config.return_value = mock_instance

            result = runner.invoke(cli, ["new"])

            assert result.exit_code == 1
            assert "No API key configured" in result.output


class TestListCommand:
    """Tests for the list command."""

    def test_list_with_no_projects(self, runner: CliRunner, _mock_home: Path) -> None:
        """List should show message when no projects exist."""
        with patch("specinit.cli.main.HistoryManager") as mock_history:
            mock_instance = MagicMock()
            mock_instance.get_recent.return_value = []
            mock_history.return_value = mock_instance

            result = runner.invoke(cli, ["list"])

            assert result.exit_code == 0
            assert "No projects generated yet" in result.output

    def test_list_shows_projects(self, runner: CliRunner, _mock_home: Path) -> None:
        """List should display project history."""
        with patch("specinit.cli.main.HistoryManager") as mock_history:
            mock_instance = MagicMock()
            mock_instance.get_recent.return_value = [
                {
                    "name": "test-project",
                    "created_at": "2025-01-01T10:00:00",
                    "path": "/tmp/test-project",
                    "cost": 1.50,
                }
            ]
            mock_history.return_value = mock_instance

            result = runner.invoke(cli, ["list"])

            assert result.exit_code == 0
            assert "test-project" in result.output
            assert "$1.50" in result.output


class TestConfigCommands:
    """Tests for config subcommands."""

    def test_config_show(self, runner: CliRunner, _mock_home: Path) -> None:
        """Config show should display current settings."""
        with patch("specinit.cli.main.ConfigManager") as mock_config:
            mock_instance = MagicMock()
            mock_instance.get_all.return_value = {
                "api_key": "sk-ant-test-12345",
                "model": "claude-sonnet-4-5-20250929",
                "cost_limit": 5.0,
                "auto_open_editor": "none",
                "auto_git_init": True,
                "projects_created": 5,
                "total_cost": 10.50,
            }
            mock_config.return_value = mock_instance

            result = runner.invoke(cli, ["config", "show"])

            assert result.exit_code == 0
            assert "claude-sonnet-4-5-20250929" in result.output
            assert "$5.00" in result.output

    def test_config_set_valid_key(self, runner: CliRunner, _mock_home: Path) -> None:
        """Config set should update valid keys."""
        with patch("specinit.cli.main.ConfigManager") as mock_config:
            mock_instance = MagicMock()
            mock_config.return_value = mock_instance

            result = runner.invoke(cli, ["config", "set", "cost_limit", "10.00"])

            assert result.exit_code == 0
            assert "Success" in result.output
            mock_instance.set.assert_called_once_with("cost_limit", 10.0)

    def test_config_set_invalid_key(self, runner: CliRunner, _mock_home: Path) -> None:
        """Config set should reject invalid keys."""
        result = runner.invoke(cli, ["config", "set", "invalid_key", "value"])

        assert result.exit_code == 1
        assert "Unknown configuration key" in result.output
