"""Configuration management for SpecInit."""

import contextlib
import logging
import os
import stat
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import keyring
import yaml

SPECINIT_SERVICE = "specinit"
CONFIG_DIR = Path.home() / ".specinit"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "api": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 100000,
    },
    "preferences": {
        "auto_open_editor": "none",
        "auto_git_init": True,
        "show_cost_warnings": True,
        "cost_limit": 5.00,
    },
    "usage": {
        "projects_created": 0,
        "total_cost": 0.0,
        "last_used": None,
    },
}


class ConfigManager:
    """Manages SpecInit configuration with secure API key storage."""

    def __init__(self) -> None:
        """Initialize the config manager."""
        self._ensure_config_dir()
        self._load_config()

    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists with proper permissions."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Set directory permissions to user-only
        CONFIG_DIR.chmod(0o700)

    def _load_config(self) -> None:
        """Load configuration from file or create defaults."""
        if CONFIG_FILE.exists():
            with CONFIG_FILE.open() as f:
                self._config = yaml.safe_load(f) or {}
            # Merge with defaults for any missing keys
            self._config = self._deep_merge(DEFAULT_CONFIG.copy(), self._config)
        else:
            self._config = DEFAULT_CONFIG.copy()
            self._save_config()

    def _save_config(self) -> None:
        """Save configuration to file."""
        with CONFIG_FILE.open("w") as f:
            yaml.dump(self._config, f, default_flow_style=False)
        # Set file permissions to user-only
        CONFIG_FILE.chmod(0o600)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get_api_key(self) -> str | None:
        """Get the API key from secure storage, file, or environment.

        Priority (highest to lowest):
        1. SPECINIT_API_KEY environment variable
        2. SPECINIT_API_KEY_FILE environment variable (file path)
        3. System keyring

        Returns:
            The API key if found, None otherwise
        """
        logger = logging.getLogger(__name__)

        # 1. Check environment variable first
        env_key = os.environ.get("SPECINIT_API_KEY")
        if env_key:
            return env_key

        # 2. Check file-based key
        key_file_path = os.environ.get("SPECINIT_API_KEY_FILE")
        if key_file_path:
            try:
                key_path = Path(key_file_path)
                if key_path.exists():
                    # Check file permissions - warn if too permissive
                    file_stat = key_path.stat()
                    file_mode = stat.S_IMODE(file_stat.st_mode)
                    if file_mode & (stat.S_IRWXG | stat.S_IRWXO):
                        logger.warning(
                            f"API key file {key_file_path} has overly permissive permissions "
                            f"({oct(file_mode)}). Consider setting to 0o600 (user read/write only)."
                        )

                    # Read and return the key
                    api_key = key_path.read_text().strip()
                    if api_key:
                        return api_key
            except Exception as e:
                logger.warning(f"Failed to read API key from file {key_file_path}: {e}")
                return None

        # 3. Try keyring
        try:
            return keyring.get_password(SPECINIT_SERVICE, "api_key")
        except Exception:
            return None

    def set_api_key(self, api_key: str) -> None:
        """Store the API key securely."""
        try:
            keyring.set_password(SPECINIT_SERVICE, "api_key", api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to store API key securely: {e}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation or simple key."""
        if key == "api_key":
            self.set_api_key(value)
            return

        # Handle simple keys by mapping to nested structure
        key_mapping = {
            "model": "api.model",
            "cost_limit": "preferences.cost_limit",
            "auto_open_editor": "preferences.auto_open_editor",
            "auto_git_init": "preferences.auto_git_init",
        }

        nested_key = key_mapping.get(key, key)
        keys = nested_key.split(".")

        # Navigate to the parent
        current = self._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value
        self._save_config()

    def get_all(self) -> dict:
        """Get all configuration as a flat dictionary."""
        result = {
            "api_key": self.get_api_key(),
            "model": self.get("api.model"),
            "cost_limit": self.get("preferences.cost_limit"),
            "auto_open_editor": self.get("preferences.auto_open_editor"),
            "auto_git_init": self.get("preferences.auto_git_init"),
            "show_cost_warnings": self.get("preferences.show_cost_warnings"),
            "projects_created": self.get("usage.projects_created"),
            "total_cost": self.get("usage.total_cost"),
            "last_used": self.get("usage.last_used"),
        }
        return result

    def update_usage(self, cost: float) -> None:
        """Update usage statistics after project generation."""
        self._config["usage"]["projects_created"] += 1
        self._config["usage"]["total_cost"] += cost
        self._config["usage"]["last_used"] = datetime.now(UTC).isoformat()
        self._save_config()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = DEFAULT_CONFIG.copy()
        self._save_config()
        # Also remove the API key
        with contextlib.suppress(Exception):
            keyring.delete_password(SPECINIT_SERVICE, "api_key")
