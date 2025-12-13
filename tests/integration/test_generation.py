"""Integration tests for project generation."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from specinit.generator.orchestrator import GenerationOrchestrator


class TestGenerationOrchestrator:
    """Integration tests for GenerationOrchestrator."""

    @pytest.fixture
    def mock_claude_response(self):
        """Create a mock Claude API response."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="# Product Spec\n\nGenerated content")]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 500
        return mock_response

    @pytest.mark.asyncio
    async def test_creates_plan_directory(self, temp_dir, mock_claude_response, monkeypatch):
        """Generation should create plan/ directory with required files."""
        # Mock dependencies
        monkeypatch.setenv("HOME", str(temp_dir))

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
        ):
            # Setup mocks
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_claude_response
            mock_anthropic.return_value = mock_client

            mock_config_instance = MagicMock()
            mock_config_instance.get_api_key.return_value = "sk-ant-test"
            mock_config_instance.get.return_value = "claude-sonnet-4-5-20250929"
            mock_config.return_value = mock_config_instance

            mock_history_instance = MagicMock()
            mock_history_instance.add_project.return_value = 1
            mock_history.return_value = mock_history_instance

            # Create orchestrator
            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run generation
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={
                    "role": "developer",
                    "action": "test generation",
                    "outcome": "verify it works",
                },
                features=["Feature 1"],
                tech_stack={
                    "frontend": ["React"],
                    "backend": ["FastAPI"],
                    "database": [],
                    "tools": [],
                },
                aesthetics=["minimalist"],
            )

            # Verify plan directory was created
            plan_dir = project_dir / "test-project" / "plan"
            assert plan_dir.exists()

            # Verify result structure
            assert "path" in result
            assert "total_cost" in result
            assert "generation_time" in result

    @pytest.mark.asyncio
    async def test_tracks_costs(self, temp_dir, mock_claude_response, monkeypatch):
        """Generation should track API costs."""
        monkeypatch.setenv("HOME", str(temp_dir))

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
        ):
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_claude_response
            mock_anthropic.return_value = mock_client

            mock_config_instance = MagicMock()
            mock_config_instance.get_api_key.return_value = "sk-ant-test"
            mock_config_instance.get.return_value = "claude-sonnet-4-5-20250929"
            mock_config.return_value = mock_config_instance

            mock_history_instance = MagicMock()
            mock_history_instance.add_project.return_value = 1
            mock_history.return_value = mock_history_instance

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            result = await orchestrator.generate(
                platforms=["web"],
                user_story={
                    "role": "developer",
                    "action": "test",
                    "outcome": "verify",
                },
                features=["Feature 1"],
                tech_stack={
                    "frontend": ["React"],
                    "backend": ["FastAPI"],
                    "database": [],
                    "tools": [],
                },
                aesthetics=["minimalist"],
            )

            # Cost should be tracked
            assert result["total_cost"] >= 0

            # History should be updated with cost
            mock_history_instance.update_project.assert_called()

    @pytest.mark.asyncio
    async def test_progress_callback_called(self, temp_dir, mock_claude_response, monkeypatch):
        """Progress callback should be called for each step."""
        monkeypatch.setenv("HOME", str(temp_dir))

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
        ):
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_claude_response
            mock_anthropic.return_value = mock_client

            mock_config_instance = MagicMock()
            mock_config_instance.get_api_key.return_value = "sk-ant-test"
            mock_config_instance.get.return_value = "claude-sonnet-4-5-20250929"
            mock_config.return_value = mock_config_instance

            mock_history_instance = MagicMock()
            mock_history_instance.add_project.return_value = 1
            mock_history.return_value = mock_history_instance

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Track progress calls
            progress_calls = []

            async def track_progress(step, status, details):
                progress_calls.append((step, status))

            await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                progress_callback=track_progress,
            )

            # Should have progress for each step (in_progress + completed)
            steps = [call[0] for call in progress_calls]
            assert "product_spec" in steps
            assert "structure" in steps
            assert "git_init" in steps
