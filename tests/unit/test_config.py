"""Tests for configuration management."""

from pathlib import Path
from unittest.mock import patch

import pytest

from specinit.storage.config import ConfigManager


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_creates_config_directory(self, mock_home):
        """Config directory should be created if it doesn't exist."""
        config = ConfigManager()

        config_dir = mock_home / ".specinit"
        assert config_dir.exists()
        assert config_dir.is_dir()

    def test_creates_default_config(self, mock_home):
        """Default config file should be created."""
        config = ConfigManager()

        config_file = mock_home / ".specinit" / "config.yaml"
        assert config_file.exists()

    def test_get_default_values(self, mock_home):
        """Default values should be returned for unset keys."""
        config = ConfigManager()

        assert config.get("api.model") == "claude-sonnet-4-5-20250929"
        assert config.get("preferences.cost_limit") == 5.00
        assert config.get("preferences.auto_git_init") is True

    def test_set_and_get_value(self, mock_home):
        """Values should be persisted and retrievable."""
        config = ConfigManager()

        config.set("cost_limit", 10.0)

        # Create new instance to verify persistence
        config2 = ConfigManager()
        assert config2.get("preferences.cost_limit") == 10.0

    def test_get_nonexistent_key_returns_default(self, mock_home):
        """Getting a nonexistent key should return the default."""
        config = ConfigManager()

        result = config.get("nonexistent.key", default="fallback")
        assert result == "fallback"

    def test_reset_restores_defaults(self, mock_home):
        """Reset should restore all default values."""
        config = ConfigManager()

        config.set("cost_limit", 100.0)
        config.reset()

        assert config.get("preferences.cost_limit") == 5.00

    def test_update_usage_increments_stats(self, mock_home):
        """Usage update should increment project count and cost."""
        config = ConfigManager()

        config.update_usage(cost=1.50)
        config.update_usage(cost=2.00)

        assert config.get("usage.projects_created") == 2
        assert config.get("usage.total_cost") == 3.50
        assert config.get("usage.last_used") is not None

    def test_get_all_returns_flat_dict(self, mock_home):
        """get_all should return a flat dictionary."""
        config = ConfigManager()

        all_config = config.get_all()

        assert "model" in all_config
        assert "cost_limit" in all_config
        assert "projects_created" in all_config

    def test_api_key_from_environment(self, mock_home, monkeypatch):
        """API key from environment should take precedence."""
        monkeypatch.setenv("SPECINIT_API_KEY", "env-api-key")

        config = ConfigManager()
        assert config.get_api_key() == "env-api-key"

    @patch("specinit.storage.config.keyring")
    def test_api_key_stored_in_keyring(self, mock_keyring, mock_home):
        """API key should be stored securely in keyring."""
        config = ConfigManager()

        config.set_api_key("sk-ant-test-key")

        mock_keyring.set_password.assert_called_once_with(
            "specinit", "api_key", "sk-ant-test-key"
        )

    @patch("specinit.storage.config.keyring")
    def test_api_key_retrieved_from_keyring(self, mock_keyring, mock_home, monkeypatch):
        """API key should be retrieved from keyring."""
        monkeypatch.delenv("SPECINIT_API_KEY", raising=False)
        mock_keyring.get_password.return_value = "stored-key"

        config = ConfigManager()

        assert config.get_api_key() == "stored-key"
