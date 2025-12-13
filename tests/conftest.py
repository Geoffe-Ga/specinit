"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_home(temp_dir, monkeypatch):
    """Mock the home directory for config tests."""
    monkeypatch.setenv("HOME", str(temp_dir))
    return temp_dir


@pytest.fixture
def mock_anthropic_client():
    """Mock the Anthropic client."""
    mock_client = MagicMock()

    # Mock message response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Generated content")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 500

    mock_client.messages.create.return_value = mock_response

    return mock_client


@pytest.fixture
def sample_project_config():
    """Sample project configuration for tests."""
    return {
        "name": "test-project",
        "platforms": ["web"],
        "user_story": {
            "role": "developer",
            "action": "quickly bootstrap projects",
            "outcome": "focus on features",
        },
        "features": ["User authentication", "Dark mode"],
        "tech_stack": {
            "frontend": ["React", "TypeScript"],
            "backend": ["FastAPI"],
            "database": ["PostgreSQL"],
            "tools": ["pytest"],
        },
        "aesthetics": ["minimalist", "professional"],
    }
