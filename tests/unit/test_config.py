"""Tests for configuration management."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specinit.storage.config import ConfigManager


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_creates_config_directory(self, mock_home: Path) -> None:
        """Config directory should be created if it doesn't exist."""
        config_dir = mock_home / ".specinit"
        config_file = config_dir / "config.yaml"

        with (
            patch("specinit.storage.config.CONFIG_DIR", config_dir),
            patch("specinit.storage.config.CONFIG_FILE", config_file),
        ):
            ConfigManager()

        assert config_dir.exists()
        assert config_dir.is_dir()

    def test_creates_default_config(self, mock_home: Path) -> None:
        """Default config file should be created."""
        config_dir = mock_home / ".specinit"
        config_file = config_dir / "config.yaml"

        with (
            patch("specinit.storage.config.CONFIG_DIR", config_dir),
            patch("specinit.storage.config.CONFIG_FILE", config_file),
        ):
            ConfigManager()

        assert config_file.exists()

    def test_get_default_values(self, _mock_home: Path) -> None:
        """Default values should be returned for unset keys."""
        # Reset config to ensure clean state
        config = ConfigManager()
        config.reset()

        assert config.get("api.model") == "claude-sonnet-4-5-20250929"
        assert config.get("preferences.cost_limit") == 5.00
        assert config.get("preferences.auto_git_init") is True

    def test_set_and_get_value(self, _mock_home: Path) -> None:
        """Values should be persisted and retrievable."""
        config = ConfigManager()

        config.set("cost_limit", 10.0)

        # Create new instance to verify persistence
        config2 = ConfigManager()
        assert config2.get("preferences.cost_limit") == 10.0

    def test_get_nonexistent_key_returns_default(self, _mock_home: Path) -> None:
        """Getting a nonexistent key should return the default."""
        config = ConfigManager()

        result = config.get("nonexistent.key", default="fallback")
        assert result == "fallback"

    def test_reset_restores_defaults(self, _mock_home: Path) -> None:
        """Reset should restore all default values."""
        config = ConfigManager()

        config.set("cost_limit", 100.0)
        config.reset()

        assert config.get("preferences.cost_limit") == 5.00

    def test_update_usage_increments_stats(self, _mock_home: Path) -> None:
        """Usage update should increment project count and cost."""
        config = ConfigManager()

        config.update_usage(cost=1.50)
        config.update_usage(cost=2.00)

        assert config.get("usage.projects_created") == 2
        assert config.get("usage.total_cost") == 3.50
        assert config.get("usage.last_used") is not None

    def test_get_all_returns_flat_dict(self, _mock_home: Path) -> None:
        """get_all should return a flat dictionary."""
        config = ConfigManager()

        all_config = config.get_all()

        assert "model" in all_config
        assert "cost_limit" in all_config
        assert "projects_created" in all_config

    def test_api_key_from_environment(
        self, _mock_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """API key from environment should take precedence."""
        monkeypatch.setenv("SPECINIT_API_KEY", "env-api-key")

        config = ConfigManager()
        assert config.get_api_key() == "env-api-key"

    @patch("specinit.storage.config.keyring")
    def test_api_key_stored_in_keyring(self, mock_keyring: MagicMock, _mock_home: Path) -> None:
        """API key should be stored securely in keyring."""
        config = ConfigManager()

        config.set_api_key("sk-ant-test-key")

        mock_keyring.set_password.assert_called_once_with("specinit", "api_key", "sk-ant-test-key")

    @patch("specinit.storage.config.keyring")
    def test_api_key_retrieved_from_keyring(
        self,
        mock_keyring: MagicMock,
        _mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """API key should be retrieved from keyring."""
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = "stored-key"

        config = ConfigManager()

        assert config.get_api_key() == "stored-key"

    @patch("specinit.storage.config.keyring")
    def test_api_key_from_file(
        self,
        mock_keyring: MagicMock,
        mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """API key should be read from file specified by SPECINIT_API_KEY_FILE."""
        # Clear env and keyring
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = None

        # Create a key file
        key_file = mock_home / "api_key.txt"
        key_file.write_text("file-based-key")

        # Set environment variable to point to the file
        monkeypatch.setenv("SPECINIT_API_KEY_FILE", str(key_file))

        config = ConfigManager()
        assert config.get_api_key() == "file-based-key"

    @patch("specinit.storage.config.keyring")
    def test_api_key_from_file_strips_whitespace(
        self,
        mock_keyring: MagicMock,
        mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """API key from file should strip leading/trailing whitespace."""
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = None

        # Create key file with whitespace
        key_file = mock_home / "api_key.txt"
        key_file.write_text("  file-key-with-spaces  \n")

        monkeypatch.setenv("SPECINIT_API_KEY_FILE", str(key_file))

        config = ConfigManager()
        assert config.get_api_key() == "file-key-with-spaces"

    @patch("specinit.storage.config.keyring")
    def test_api_key_from_nonexistent_file_returns_none(
        self,
        mock_keyring: MagicMock,
        mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should return None if API key file doesn't exist."""
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = None

        # Point to non-existent file
        monkeypatch.setenv("SPECINIT_API_KEY_FILE", str(mock_home / "nonexistent.txt"))

        config = ConfigManager()
        assert config.get_api_key() is None

    @patch("specinit.storage.config.keyring")
    def test_api_key_priority_env_over_file(
        self,
        mock_keyring: MagicMock,
        mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """SPECINIT_API_KEY environment variable should take precedence over file."""
        mock_keyring.get_password.return_value = None

        # Create key file
        key_file = mock_home / "api_key.txt"
        key_file.write_text("file-key")

        # Set both environment variables
        monkeypatch.setenv("SPECINIT_API_KEY", "env-key")
        monkeypatch.setenv("SPECINIT_API_KEY_FILE", str(key_file))

        config = ConfigManager()
        # Env var should take precedence
        assert config.get_api_key() == "env-key"

    @patch("specinit.storage.config.keyring")
    def test_api_key_priority_file_over_keyring(
        self,
        mock_keyring: MagicMock,
        mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """File-based key should take precedence over keyring."""
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = "keyring-key"

        # Create key file
        key_file = mock_home / "api_key.txt"
        key_file.write_text("file-key")

        monkeypatch.setenv("SPECINIT_API_KEY_FILE", str(key_file))

        config = ConfigManager()
        # File should take precedence over keyring
        assert config.get_api_key() == "file-key"

    @patch("specinit.storage.config.keyring")
    def test_api_key_from_file_with_restrictive_permissions_warning(
        self,
        mock_keyring: MagicMock,
        mock_home: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Should warn if API key file has overly permissive permissions."""
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = None

        # Create key file with world-readable permissions
        key_file = mock_home / "api_key.txt"
        key_file.write_text("file-key")
        key_file.chmod(0o644)  # World-readable

        monkeypatch.setenv("SPECINIT_API_KEY_FILE", str(key_file))

        with caplog.at_level(logging.WARNING):
            config = ConfigManager()
            _ = config.get_api_key()

        # Should warn about permissions
        assert any("permissions" in record.message.lower() for record in caplog.records)
