"""Integration tests for project generation."""

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from specinit.generator.orchestrator import GenerationOrchestrator


def configure_git_in_temp_home(temp_dir: Path) -> None:
    """Configure git user in a temp HOME directory.

    When tests change HOME to a temp directory, git looks for ~/.gitconfig
    there. This function sets up git config in the temp HOME so git commands
    don't fail with "Author identity unknown" errors.
    """
    subprocess.run(
        ["git", "config", "--global", "user.email", "test@specinit.test"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--global", "user.name", "Test Runner"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )


class TestGenerationOrchestrator:
    """Integration tests for GenerationOrchestrator."""

    @pytest.fixture
    def mock_claude_response(self) -> MagicMock:
        """Create a mock Claude API response."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="# Product Spec\n\nGenerated content")]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 500
        return mock_response

    @pytest.mark.asyncio
    async def test_creates_plan_directory(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Generation should create plan/ directory with required files."""
        # Mock dependencies
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

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
    async def test_tracks_costs(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Generation should track API costs."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

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
    async def test_progress_callback_called(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Progress callback should be called for each step."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

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
            progress_calls: list[tuple[str, str]] = []

            async def track_progress(
                step: str, status: str, _details: dict[str, Any] | None
            ) -> None:
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

    @pytest.mark.asyncio
    async def test_github_integration_disabled_when_not_configured(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should not run when not configured."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh,
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

            # Run without GitHub config
            await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config=None,  # No GitHub config
            )

            # GitHub service should NOT be called
            mock_gh.get_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_github_integration_creates_repo_and_issues(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should create repo, push commit, and create issues."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
            patch("specinit.generator.orchestrator.subprocess") as mock_subprocess,
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

            # Mock GitHub service
            mock_gh_class.get_token.return_value = "ghp_test_token"
            mock_gh = MagicMock()
            mock_gh.parse_repo_url.return_value = ("testowner", "testrepo")
            mock_gh.repo_exists.return_value = False
            # Make the mock work as a context manager
            mock_gh.__enter__.return_value = mock_gh
            mock_gh.__exit__.return_value = None
            mock_gh_class.return_value = mock_gh

            # Mock subprocess for git operations
            # Need to handle both git init (step 7) and GitHub push operations
            def subprocess_side_effect(*args, **kwargs):
                cmd = args[0] if args else kwargs.get("args", [])
                result = MagicMock()
                result.stderr = b""

                # Return code 1 only for "git remote get-url", 0 for everything else
                result.returncode = 1 if cmd[0:3] == ["git", "remote", "get-url"] else 0
                return result

            mock_subprocess.run.side_effect = subprocess_side_effect

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Track progress calls
            progress_calls: list[tuple[str, str]] = []

            async def track_progress(
                step: str, status: str, _details: dict[str, Any] | None
            ) -> None:
                progress_calls.append((step, status))

            # Run with GitHub config
            await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature 1", "Feature 2"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "https://github.com/testowner/testrepo",
                    "create_repo": True,
                    "yolo_mode": False,
                },
                progress_callback=track_progress,
            )

            # GitHub service should be called
            mock_gh_class.get_token.assert_called_once()
            mock_gh.parse_repo_url.assert_called_once_with("https://github.com/testowner/testrepo")
            mock_gh.repo_exists.assert_called_once_with("testowner", "testrepo")
            mock_gh.create_repo.assert_called_once()

            # Issues should be created for each feature
            assert mock_gh.create_issue.call_count == 2

            # Progress should include github_setup
            steps = [call[0] for call in progress_calls]
            assert "github_setup" in steps

    @pytest.mark.asyncio
    async def test_github_integration_handles_errors_gracefully(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration errors should not fail the entire generation."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

            # Mock GitHub service to raise an error
            mock_gh_class.get_token.return_value = "ghp_test_token"
            mock_gh = MagicMock()
            mock_gh.parse_repo_url.side_effect = ValueError("Invalid repo URL")
            mock_gh_class.return_value = mock_gh

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run with GitHub config that will fail
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "invalid-url",
                    "create_repo": True,
                },
            )

            # Generation should still succeed despite GitHub error
            assert "path" in result
            assert "total_cost" in result

    @pytest.mark.asyncio
    async def test_github_integration_validates_url_security(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should reject URLs that could cause command injection."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

            # Mock GitHub service
            mock_gh_class.get_token.return_value = "ghp_test_token"

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run with malicious repo URL (starts with dash)
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "--flag-injection",
                    "create_repo": True,
                },
            )

            # Generation should succeed but skip GitHub integration
            assert "path" in result
            # GitHubService should not be instantiated due to security check
            mock_gh_class.assert_not_called()

    @pytest.mark.asyncio
    async def test_github_integration_handles_repo_creation_failure(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should handle repo creation failure gracefully."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

            # Mock GitHub service
            mock_gh_class.get_token.return_value = "ghp_test_token"
            mock_gh = MagicMock()
            mock_gh.parse_repo_url.return_value = ("testowner", "testrepo")
            mock_gh.repo_exists.return_value = False
            # Make repo creation fail
            mock_gh.create_repo.side_effect = Exception("API Error")
            mock_gh.__enter__.return_value = mock_gh
            mock_gh.__exit__.return_value = None
            mock_gh_class.return_value = mock_gh

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run with GitHub config that will fail on repo creation
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "https://github.com/testowner/testrepo",
                    "create_repo": True,
                },
            )

            # Generation should succeed despite GitHub failure
            assert "path" in result
            # Repo creation should have been attempted
            mock_gh.create_repo.assert_called_once()

    @pytest.mark.asyncio
    async def test_github_integration_handles_missing_token(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should handle missing token gracefully."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

            # Mock GitHub service - return None for get_token
            mock_gh_class.get_token.return_value = None

            project_dir = temp_dir / "output"
            project_dir.mkdir()

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run with GitHub config but missing token
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "https://github.com/testowner/testrepo",
                    "create_repo": True,
                },
            )

            # Generation should succeed but skip GitHub
            assert "path" in result
            # get_token should be called, but GitHubService not instantiated
            mock_gh_class.get_token.assert_called_once()
            # GitHubService constructor should NOT be called
            assert mock_gh_class.call_count == 0

    @pytest.mark.asyncio
    async def test_github_integration_rejects_dangerous_url_characters(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should reject URLs with dangerous shell characters."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        dangerous_urls = [
            "https://github.com/owner/repo;rm -rf /",
            "https://github.com/owner/repo&malicious",
            "https://github.com/owner/repo|cat /etc/passwd",
            "https://github.com/owner/repo`whoami`",
            "https://github.com/owner/repo$(id)",
            "-dash-prefix-attack",
        ]

        for idx, dangerous_url in enumerate(dangerous_urls):
            with (
                patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
                patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
                patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
                patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

                # Mock GitHub service
                mock_gh_class.get_token.return_value = "ghp_test123"

                project_dir = temp_dir / f"output-dangerous-{idx}"
                project_dir.mkdir(exist_ok=True)

                orchestrator = GenerationOrchestrator(
                    output_dir=project_dir,
                    project_name="test-project",
                )

                # Run with dangerous URL
                result = await orchestrator.generate(
                    platforms=["web"],
                    user_story={"role": "dev", "action": "test", "outcome": "verify"},
                    features=["Feature"],
                    tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                    aesthetics=[],
                    github_config={
                        "enabled": True,
                        "repo_url": dangerous_url,
                        "create_repo": True,
                    },
                )

                # Generation should succeed
                assert "path" in result
                # GitHubService should NOT be instantiated due to validation failure
                assert mock_gh_class.call_count == 0

    @pytest.mark.asyncio
    async def test_github_integration_handles_network_errors(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should handle network errors gracefully."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

            # Mock GitHub service to raise network error
            mock_gh_class.get_token.return_value = "ghp_test123"
            mock_gh = MagicMock()
            mock_gh.parse_repo_url.return_value = ("owner", "repo")
            mock_gh.repo_exists.side_effect = requests.exceptions.ConnectionError("Network error")
            mock_gh.__enter__.return_value = mock_gh
            mock_gh.__exit__.return_value = None
            mock_gh_class.return_value = mock_gh

            project_dir = temp_dir / "output-network"
            project_dir.mkdir(exist_ok=True)

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run with network error scenario
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "https://github.com/owner/repo",
                    "create_repo": True,
                },
            )

            # Generation should still succeed despite network error
            assert "path" in result
            # parse_repo_url should have been called
            mock_gh.parse_repo_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_github_integration_handles_missing_repo_url(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should handle missing repo URL gracefully."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
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

            # Mock GitHub service
            mock_gh_class.get_token.return_value = "ghp_test123"

            project_dir = temp_dir / "output-no-url"
            project_dir.mkdir(exist_ok=True)

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run with empty repo_url
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "",  # Empty URL
                    "create_repo": True,
                },
            )

            # Generation should succeed but skip GitHub
            assert "path" in result
            # GitHubService should NOT be instantiated
            assert mock_gh_class.call_count == 0

    async def test_github_integration_handles_git_push_failure(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should handle git push failures gracefully."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
            patch("subprocess.run") as mock_subprocess,
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

            # Mock GitHub service
            mock_gh = MagicMock()
            mock_gh.parse_repo_url.return_value = ("owner", "repo")
            mock_gh.repo_exists.return_value = False
            mock_gh.__enter__.return_value = mock_gh
            mock_gh.__exit__.return_value = None
            mock_gh_class.return_value = mock_gh
            mock_gh_class.get_token.return_value = "ghp_test123"

            # Mock subprocess to fail on git push
            def subprocess_side_effect(*args, **kwargs):
                cmd = args[0] if args else kwargs.get("args", [])
                if "push" in cmd:
                    raise subprocess.CalledProcessError(1, cmd, stderr=b"Authentication failed")
                # Return 128 (error) for get-url check, 0 (success) for everything else
                if len(cmd) > 2 and cmd[2] == "get-url":
                    return MagicMock(returncode=128, stdout=b"", stderr=b"")
                return MagicMock(returncode=0, stdout=b"", stderr=b"")

            mock_subprocess.side_effect = subprocess_side_effect

            project_dir = temp_dir / "output-push-fail"
            project_dir.mkdir(exist_ok=True)

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run generation
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "https://github.com/owner/repo",
                    "create_repo": True,
                },
            )

            # Generation should succeed despite push failure
            assert "path" in result

    async def test_github_integration_updates_existing_remote(
        self,
        temp_dir: Path,
        mock_claude_response: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """GitHub integration should update existing git remote."""
        monkeypatch.setenv("HOME", str(temp_dir))
        configure_git_in_temp_home(temp_dir)

        with (
            patch("specinit.generator.orchestrator.Anthropic") as mock_anthropic,
            patch("specinit.generator.orchestrator.ConfigManager") as mock_config,
            patch("specinit.generator.orchestrator.HistoryManager") as mock_history,
            patch("specinit.generator.orchestrator.GitHubService") as mock_gh_class,
            patch("subprocess.run") as mock_subprocess,
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

            # Mock GitHub service
            mock_gh = MagicMock()
            mock_gh.parse_repo_url.return_value = ("owner", "repo")
            mock_gh.repo_exists.return_value = True
            mock_gh.__enter__.return_value = mock_gh
            mock_gh.__exit__.return_value = None
            mock_gh_class.return_value = mock_gh
            mock_gh_class.get_token.return_value = "ghp_test123"

            # Track git remote set-url calls
            set_url_called = []

            # Mock subprocess - simulate existing remote
            def subprocess_side_effect(*args, **kwargs):
                cmd = args[0] if args else kwargs.get("args", [])
                if "get-url" in cmd:
                    # Remote exists
                    return MagicMock(
                        returncode=0, stdout=b"https://github.com/old/repo", stderr=b""
                    )
                if "set-url" in cmd:
                    set_url_called.append(cmd)
                    return MagicMock(returncode=0, stdout=b"", stderr=b"")
                # Success for other commands
                return MagicMock(returncode=0, stdout=b"", stderr=b"")

            mock_subprocess.side_effect = subprocess_side_effect

            project_dir = temp_dir / "output-update-remote"
            project_dir.mkdir(exist_ok=True)

            orchestrator = GenerationOrchestrator(
                output_dir=project_dir,
                project_name="test-project",
            )

            # Run generation
            result = await orchestrator.generate(
                platforms=["web"],
                user_story={"role": "dev", "action": "test", "outcome": "verify"},
                features=["Feature"],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
                github_config={
                    "enabled": True,
                    "repo_url": "https://github.com/owner/repo",
                    "create_repo": False,  # Repo already exists
                },
            )

            # Generation should succeed
            assert "path" in result
            # Should have called set-url to update remote
            assert len(set_url_called) > 0
            assert "set-url" in set_url_called[0]
