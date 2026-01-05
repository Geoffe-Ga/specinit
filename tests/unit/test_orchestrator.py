"""Tests for generation orchestrator context accumulation."""

from unittest.mock import MagicMock, patch

import pytest

from specinit.generator.orchestrator import GenerationOrchestrator


class TestContextAccumulation:
    """Tests for step-aware context accumulation."""

    @pytest.fixture
    def orchestrator(self, temp_dir):
        """Create orchestrator instance with mocked dependencies."""
        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager", autospec=False) as mock_history,
        ):
            # Mock Anthropic client
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            mock_response.content = [MagicMock(text="Generated content")]
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            # Mock ConfigManager
            mock_config_instance = MagicMock()
            mock_config_instance.get_api_key.return_value = "sk-ant-test"
            mock_config_instance.get.return_value = "claude-sonnet-4-5-20250929"
            mock_config.return_value = mock_config_instance

            # Mock HistoryManager - prevent real __init__ from running
            mock_history_instance = MagicMock()
            mock_history.return_value = mock_history_instance

            orchestrator = GenerationOrchestrator(output_dir=temp_dir, project_name="test-project")
            yield orchestrator

    def test_read_previous_step_outputs_returns_dict(self, orchestrator):
        """Should return a dictionary of file paths and contents from previous steps."""
        # Create some files to simulate previous steps
        (orchestrator.project_path / "plan").mkdir(parents=True, exist_ok=True)
        spec_path = orchestrator.project_path / "plan" / "product-spec.md"
        spec_path.write_text("# Product Specification\n\nThis is the spec.")

        # Read outputs
        outputs = orchestrator._read_previous_step_outputs()

        assert isinstance(outputs, dict)
        assert "plan/product-spec.md" in outputs
        assert "# Product Specification" in outputs["plan/product-spec.md"]

    def test_read_previous_step_outputs_skips_excluded_files(self, orchestrator):
        """Should skip common build/cache directories."""
        # Create files that should be skipped
        (orchestrator.project_path / ".git").mkdir(parents=True, exist_ok=True)
        (orchestrator.project_path / ".git" / "config").write_text("git config")

        (orchestrator.project_path / "node_modules").mkdir(parents=True, exist_ok=True)
        (orchestrator.project_path / "node_modules" / "package.json").write_text("{}")

        # Create files that should be included
        (orchestrator.project_path / "plan").mkdir(parents=True, exist_ok=True)
        (orchestrator.project_path / "plan" / "spec.md").write_text("spec")

        outputs = orchestrator._read_previous_step_outputs()

        # Should include plan files
        assert "plan/spec.md" in outputs

        # Should exclude .git and node_modules
        assert not any(".git" in path for path in outputs)
        assert not any("node_modules" in path for path in outputs)

    def test_read_previous_step_outputs_limits_file_size(self, orchestrator):
        """Should truncate very large files to prevent context overflow."""
        (orchestrator.project_path / "plan").mkdir(parents=True, exist_ok=True)
        large_file = orchestrator.project_path / "plan" / "large.md"

        # Create a file larger than the limit (assuming 50KB limit)
        large_content = "x" * 100_000  # 100KB
        large_file.write_text(large_content)

        outputs = orchestrator._read_previous_step_outputs()

        # Should include the file but truncate it
        assert "plan/large.md" in outputs
        assert len(outputs["plan/large.md"]) < len(large_content)
        assert "[Truncated" in outputs["plan/large.md"]

    def test_build_step_context_includes_previous_outputs(self, orchestrator):
        """Should build context that includes outputs from previous steps."""
        # Create some previous step outputs
        (orchestrator.project_path / "plan").mkdir(parents=True, exist_ok=True)
        spec_path = orchestrator.project_path / "plan" / "product-spec.md"
        spec_path.write_text("# Spec\n\nFeature list")

        base_context = {
            "project_name": "test",
            "platforms": ["web"],
            "features": ["Feature 1"],
        }

        step_context = orchestrator._build_step_context("documentation", base_context)

        assert "project_name" in step_context
        assert "previous_outputs" in step_context
        assert "plan/product-spec.md" in step_context["previous_outputs"]
        assert "Feature list" in step_context["previous_outputs"]["plan/product-spec.md"]

    def test_build_step_context_for_first_step_has_no_previous_outputs(self, orchestrator):
        """Should not include previous outputs for the first step (product_spec)."""
        base_context = {
            "project_name": "test",
            "platforms": ["web"],
        }

        step_context = orchestrator._build_step_context("product_spec", base_context)

        # First step should not have previous_outputs
        assert "previous_outputs" not in step_context or step_context["previous_outputs"] == {}

    def test_build_step_context_includes_only_relevant_previous_steps(self, orchestrator):
        """Should only include outputs from steps that came before the current step."""
        # Create files from multiple steps
        (orchestrator.project_path / "plan").mkdir(parents=True, exist_ok=True)
        (orchestrator.project_path / "plan" / "product-spec.md").write_text("Spec")
        (orchestrator.project_path / "plan" / "progress-notes.md").write_text("Progress")
        (orchestrator.project_path / "src").mkdir(parents=True, exist_ok=True)
        (orchestrator.project_path / "src" / "main.py").write_text("# Future code")

        base_context = {"project_name": "test"}

        # At the "structure" step (step 2), we should only see product_spec outputs
        step_context = orchestrator._build_step_context("structure", base_context)

        assert "previous_outputs" in step_context
        # Should include plan files but not src files (structure creates src)
        assert "plan/product-spec.md" in step_context["previous_outputs"]

    @pytest.mark.asyncio
    async def test_execute_step_uses_accumulated_context(self, orchestrator):
        """Should pass accumulated context when calling Claude API."""
        # Create a previous step output
        (orchestrator.project_path / "plan").mkdir(parents=True, exist_ok=True)
        (orchestrator.project_path / "plan" / "product-spec.md").write_text(
            "# Specification\n\nDetailed spec content"
        )

        base_context = {
            "project_name": "test",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": ["minimalist"],
            "template": {"name": "test-template"},
        }

        with patch.object(orchestrator, "_call_claude", return_value="Generated docs"):
            await orchestrator._execute_step("documentation", base_context)

            # Verify _call_claude was called
            orchestrator._call_claude.assert_called_once()

            # Get the prompt that was passed
            call_args = orchestrator._call_claude.call_args
            prompt = call_args[0][0]

            # Prompt should reference the product spec content
            assert "Specification" in prompt or "product-spec.md" in prompt

    def test_read_previous_step_outputs_handles_binary_files(self, orchestrator):
        """Should skip binary files that can't be read as text."""
        (orchestrator.project_path / "assets").mkdir(parents=True, exist_ok=True)
        binary_file = orchestrator.project_path / "assets" / "image.png"
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")

        outputs = orchestrator._read_previous_step_outputs()

        # Should not include binary files
        assert "assets/image.png" not in outputs

    def test_read_previous_step_outputs_handles_empty_directory(self, orchestrator):
        """Should handle empty project directory gracefully."""
        outputs = orchestrator._read_previous_step_outputs()

        assert isinstance(outputs, dict)
        assert len(outputs) == 0
