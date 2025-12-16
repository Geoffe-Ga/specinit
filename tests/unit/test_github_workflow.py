"""Tests for GitHub workflow orchestration."""

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from specinit.github.service import Issue, PullRequest
from specinit.github.workflow import (
    CoverageThresholds,
    GitHubConfig,
    GitHubWorkflow,
    IssueStatus,
    WorkflowIssue,
)


class TestGitHubWorkflow:
    """Tests for GitHubWorkflow."""

    @pytest.fixture
    def mock_github_service(self) -> MagicMock:
        """Create a mock GitHub service."""
        service = MagicMock()
        service.create_label = MagicMock()
        service.create_milestone.return_value = 1
        service.create_issue.return_value = Issue(
            number=1,
            title="Test Issue",
            body="Test body",
            labels=["specinit"],
            state="open",
            url="https://github.com/user/repo/issues/1",
        )
        service.create_pull_request.return_value = PullRequest(
            number=1,
            title="Test PR",
            body="Test body",
            head="feature-branch",
            base="main",
            state="open",
            url="https://github.com/user/repo/pull/1",
        )
        service.get_pr_checks.return_value = {
            "check_runs": [
                {"status": "completed", "conclusion": "success"},
            ]
        }
        service.get_pr_reviews.return_value = [{"state": "APPROVED"}]
        service.get_pr_comments.return_value = []
        service.merge_pull_request.return_value = True
        return service

    @pytest.fixture
    def github_config(self) -> GitHubConfig:
        """Create a test GitHub config."""
        return GitHubConfig(
            owner="testuser",
            repo="testrepo",
            base_branch="main",
            auto_merge=True,
            yolo_mode=False,
            max_fix_attempts=3,
            parallel_branches=2,
        )

    @pytest.fixture
    def workflow(
        self,
        github_config: GitHubConfig,
        mock_github_service: MagicMock,
        temp_dir: Path,
    ) -> GitHubWorkflow:
        """Create a test workflow."""
        return GitHubWorkflow(
            config=github_config,
            project_path=temp_dir,
            github_service=mock_github_service,
        )

    @pytest.mark.asyncio
    async def test_setup_repository_creates_labels(
        self, workflow: GitHubWorkflow, mock_github_service: MagicMock
    ) -> None:
        """Should create labels when setting up repository."""
        await workflow.setup_repository()

        # Should create multiple labels
        assert mock_github_service.create_label.call_count >= 5

    @pytest.mark.asyncio
    async def test_create_milestone(
        self, workflow: GitHubWorkflow, mock_github_service: MagicMock
    ) -> None:
        """Should create a milestone."""
        milestone_number = await workflow.create_milestone("v1.0.0", "Initial release")

        assert milestone_number == 1
        mock_github_service.create_milestone.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_issues_from_spec(
        self, workflow: GitHubWorkflow, _mock_github_service: MagicMock
    ) -> None:
        """Should create issues based on spec."""
        issues = await workflow.create_issues_from_spec(
            _spec_content="Test spec",
            features=["Feature 1", "Feature 2"],
            user_story={"role": "user", "action": "test", "outcome": "result"},
        )

        # Should create setup issues + feature issues + test issue
        # 4 setup + 2 features + 1 test = 7 issues
        assert len(issues) >= 5

    def test_get_ready_issues_no_dependencies(self, workflow: GitHubWorkflow) -> None:
        """Should return issues with no dependencies."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(issue=issue1, dependencies=[])
        workflow.issues[2] = WorkflowIssue(issue=issue2, dependencies=[])

        ready = workflow.get_ready_issues()

        assert len(ready) == 2

    def test_get_ready_issues_with_dependencies(self, workflow: GitHubWorkflow) -> None:
        """Should not return issues with unmet dependencies."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(issue=issue1, dependencies=[], status=IssueStatus.QUEUED)
        workflow.issues[2] = WorkflowIssue(
            issue=issue2, dependencies=[1], status=IssueStatus.QUEUED
        )

        ready = workflow.get_ready_issues()

        # Only issue 1 should be ready (issue 2 depends on 1)
        assert len(ready) == 1
        assert ready[0].issue.number == 1

    def test_get_ready_issues_after_merge(self, workflow: GitHubWorkflow) -> None:
        """Should return dependent issues after dependency is merged."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(issue=issue1, dependencies=[], status=IssueStatus.MERGED)
        workflow.issues[2] = WorkflowIssue(
            issue=issue2, dependencies=[1], status=IssueStatus.QUEUED
        )

        ready = workflow.get_ready_issues()

        # Issue 2 should now be ready since issue 1 is merged
        assert len(ready) == 1
        assert ready[0].issue.number == 2

    def test_get_status_summary(self, workflow: GitHubWorkflow) -> None:
        """Should return correct status summary."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")
        issue3 = Issue(3, "Issue 3", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(issue=issue1, status=IssueStatus.MERGED)
        workflow.issues[2] = WorkflowIssue(issue=issue2, status=IssueStatus.IN_PROGRESS)
        workflow.issues[3] = WorkflowIssue(issue=issue3, status=IssueStatus.QUEUED)

        summary = workflow.get_status_summary()

        assert summary["total_issues"] == 3
        assert summary["merged"] == 1
        assert summary["in_progress"] == 1

    def test_slugify(self, workflow: GitHubWorkflow) -> None:
        """Should create URL-safe slugs."""
        assert workflow._slugify("[Setup] Initialize project") == "setup-initialize-project"
        assert workflow._slugify("[Feature] Add dark mode!") == "feature-add-dark-mode"
        assert workflow._slugify("Test   Multiple   Spaces") == "test-multiple-spaces"

    @pytest.mark.asyncio
    async def test_work_on_issue_creates_branch_and_pr(
        self,
        workflow: GitHubWorkflow,
        mock_github_service: MagicMock,
        temp_dir: Path,
    ) -> None:
        """Should create branch and PR when working on issue."""
        issue = Issue(1, "[Setup] Test Issue", "Body", ["specinit"], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)
        workflow.issues[1] = workflow_issue

        async def mock_implementation(_issue: Issue) -> None:
            # Create a test file
            (temp_dir / "test.txt").write_text("test content")

        with (
            patch("specinit.github.workflow.create_branch"),
            patch("specinit.github.workflow.push_branch"),
            patch("subprocess.run") as mock_run,
        ):
            # Pre-commit passes, all git commands succeed
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            await workflow.work_on_issue(workflow_issue, mock_implementation)

        # Should have created a PR
        mock_github_service.create_pull_request.assert_called()


class TestIssueStatus:
    """Tests for IssueStatus enum."""

    def test_all_statuses_defined(self) -> None:
        """All expected statuses should be defined."""
        expected = [
            "queued",
            "in_progress",
            "precommit_failed",
            "precommit_fixing",
            "pr_created",
            "ci_running",
            "ci_failed",
            "ci_fixing",
            "coverage_failed",
            "coverage_fixing",
            "in_review",
            "changes_requested",
            "review_fixing",
            "approved",
            "merged",
            "blocked",
            "failed",
        ]

        for status in expected:
            assert hasattr(IssueStatus, status.upper())


class TestWorkflowIssue:
    """Tests for WorkflowIssue dataclass."""

    def test_default_values(self) -> None:
        """Should have correct default values."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        assert workflow_issue.status == IssueStatus.QUEUED
        assert workflow_issue.branch_name == ""
        assert workflow_issue.pr is None
        assert workflow_issue.dependencies == []
        assert workflow_issue.fix_attempts == 0
        assert workflow_issue.error_message == ""


class TestRunPrecommit:
    """Tests for _run_precommit method."""

    @pytest.fixture
    def workflow_with_project(self, temp_dir: Path) -> GitHubWorkflow:
        """Create workflow with a project path."""
        config = GitHubConfig(owner="testuser", repo="testrepo")
        service = MagicMock()
        return GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

    @pytest.mark.asyncio
    async def test_precommit_success(self, workflow_with_project: GitHubWorkflow) -> None:
        """Should return True when pre-commit succeeds."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = await workflow_with_project._run_precommit(workflow_issue)

        assert result is True
        assert workflow_issue.fix_attempts == 0

    @pytest.mark.asyncio
    async def test_precommit_failure(self, workflow_with_project: GitHubWorkflow) -> None:
        """Should return False and increment attempts on failure."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="Linting failed",
                stderr="Error in file.py",
            )
            result = await workflow_with_project._run_precommit(workflow_issue)

        assert result is False
        assert workflow_issue.fix_attempts == 1
        assert "Linting failed" in workflow_issue.error_message


class TestWaitForCI:
    """Tests for _wait_for_ci method."""

    @pytest.fixture
    def workflow_with_mocks(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow with mock service."""
        config = GitHubConfig(owner="testuser", repo="testrepo")
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_ci_passes_immediately(
        self, workflow_with_mocks: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should set IN_REVIEW when CI passes."""
        workflow, service = workflow_with_mocks
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "success"}]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        await workflow._wait_for_ci(workflow_issue)

        assert workflow_issue.status == IssueStatus.IN_REVIEW

    @pytest.mark.asyncio
    async def test_ci_fails(self, workflow_with_mocks: tuple[GitHubWorkflow, MagicMock]) -> None:
        """Should set CI_FAILED when checks fail."""
        workflow, service = workflow_with_mocks
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "failure"}]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        await workflow._wait_for_ci(workflow_issue)

        assert workflow_issue.status == IssueStatus.CI_FAILED

    @pytest.mark.asyncio
    async def test_ci_no_pr(self, workflow_with_mocks: tuple[GitHubWorkflow, MagicMock]) -> None:
        """Should return early when no PR."""
        workflow, _service = workflow_with_mocks

        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=None)

        await workflow._wait_for_ci(workflow_issue)

        # Status is set to CI_RUNNING before PR check, then returns
        assert workflow_issue.status == IssueStatus.CI_RUNNING

    @pytest.mark.asyncio
    async def test_ci_with_progress_callback(
        self, workflow_with_mocks: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should call progress callback when CI is running."""
        workflow, service = workflow_with_mocks
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "success"}]
        }

        callback_calls: list[tuple] = []

        async def mock_callback(issue_id: str, status: str, data: dict | None) -> None:
            callback_calls.append((issue_id, status, data))

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        await workflow._wait_for_ci(workflow_issue, mock_callback)

        assert len(callback_calls) >= 1
        assert callback_calls[0][1] == "ci_running"


class TestHandleReviews:
    """Tests for _handle_reviews method."""

    @pytest.fixture
    def workflow_for_reviews(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow configured for review handling."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            yolo_mode=True,
            max_fix_attempts=2,
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_review_approved(
        self, workflow_for_reviews: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should set APPROVED when review is approved."""
        workflow, service = workflow_for_reviews
        service.get_pr_reviews.return_value = [{"state": "APPROVED"}]
        service.get_pr_comments.return_value = []

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        await workflow._handle_reviews(workflow_issue, mock_impl)

        assert workflow_issue.status == IssueStatus.APPROVED

    @pytest.mark.asyncio
    async def test_review_no_explicit_approval_no_blockers(
        self, workflow_for_reviews: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should set APPROVED when no blockers even without explicit approval."""
        workflow, service = workflow_for_reviews
        service.get_pr_reviews.return_value = []  # No reviews
        service.get_pr_comments.return_value = []  # No comments

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        await workflow._handle_reviews(workflow_issue, mock_impl)

        assert workflow_issue.status == IssueStatus.APPROVED

    @pytest.mark.asyncio
    async def test_review_no_pr(
        self, workflow_for_reviews: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should return early when no PR exists."""
        workflow, _service = workflow_for_reviews

        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=None)

        async def mock_impl(_issue: Issue) -> None:
            pass

        await workflow._handle_reviews(workflow_issue, mock_impl)

        # Status should remain unchanged
        assert workflow_issue.status == IssueStatus.QUEUED


class TestRunParallel:
    """Tests for run_parallel method."""

    @pytest.mark.asyncio
    async def test_run_parallel_no_issues(self, temp_dir: Path) -> None:
        """Should complete immediately with no issues."""
        config = GitHubConfig(owner="testuser", repo="testrepo")
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

        async def mock_impl(_issue: Issue) -> None:
            pass

        # Should complete without error
        await workflow.run_parallel(mock_impl)

    @pytest.mark.asyncio
    async def test_run_parallel_gets_ready_issues(self, temp_dir: Path) -> None:
        """Should get ready issues and attempt to process them."""
        config = GitHubConfig(owner="testuser", repo="testrepo", parallel_branches=2)
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

        # Add issues - one merged (not ready), one queued with unsatisfied dep
        issue1 = Issue(1, "Done", "", [], "open", "")
        issue2 = Issue(2, "Pending", "", [], "open", "")
        workflow.issues[1] = WorkflowIssue(issue=issue1, dependencies=[], status=IssueStatus.MERGED)
        workflow.issues[2] = WorkflowIssue(
            issue=issue2, dependencies=[1], status=IssueStatus.QUEUED
        )

        # Mock work_on_issue to avoid slow async operations
        async def mock_work(_issue: WorkflowIssue, _impl: Any, _callback: Any = None) -> None:
            _issue.status = IssueStatus.MERGED

        async def mock_impl(_issue: Issue) -> None:
            pass

        with patch.object(workflow, "work_on_issue", mock_work):
            await workflow.run_parallel(mock_impl)

        # Issue 2 should have been processed (its dep issue 1 is merged)
        assert workflow.issues[2].status == IssueStatus.MERGED


class TestWorkOnIssueEdgeCases:
    """Tests for work_on_issue edge cases."""

    @pytest.fixture
    def workflow_for_edge_cases(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow for testing edge cases."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            auto_merge=True,
            yolo_mode=True,
            max_fix_attempts=1,
        )
        service = MagicMock()
        service.create_pull_request.return_value = PullRequest(
            1, "PR", "", "branch", "main", "open", ""
        )
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "success"}]
        }
        service.get_pr_reviews.return_value = [{"state": "APPROVED"}]
        service.get_pr_comments.return_value = []
        service.merge_pull_request.return_value = True

        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_work_on_issue_branch_exists(
        self, workflow_for_edge_cases: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should checkout existing branch if create fails."""
        workflow, _service = workflow_for_edge_cases

        issue = Issue(1, "[Test] Issue", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)
        workflow.issues[1] = workflow_issue

        async def mock_impl(_issue: Issue) -> None:
            pass

        with (
            patch("specinit.github.workflow.create_branch") as mock_create,
            patch("specinit.github.workflow.push_branch"),
            patch("subprocess.run") as mock_run,
        ):
            # First call to create_branch raises CalledProcessError
            mock_create.side_effect = subprocess.CalledProcessError(1, "git")
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            await workflow.work_on_issue(workflow_issue, mock_impl)

        # Should have called git checkout for the existing branch
        checkout_calls = [c for c in mock_run.call_args_list if "checkout" in str(c)]
        assert len(checkout_calls) > 0

    @pytest.mark.asyncio
    async def test_work_on_issue_with_progress_callback(
        self, workflow_for_edge_cases: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should call progress callback at various stages."""
        workflow, _service = workflow_for_edge_cases

        issue = Issue(1, "[Test] Issue", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)
        workflow.issues[1] = workflow_issue

        callback_calls: list[tuple] = []

        async def mock_callback(issue_id: str, status: str, data: dict | None) -> None:
            callback_calls.append((issue_id, status, data))

        async def mock_impl(_issue: Issue) -> None:
            pass

        with (
            patch("specinit.github.workflow.create_branch"),
            patch("specinit.github.workflow.push_branch"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            await workflow.work_on_issue(workflow_issue, mock_impl, mock_callback)

        # Should have called callback for in_progress and other stages
        statuses = [c[1] for c in callback_calls]
        assert "in_progress" in statuses

    @pytest.mark.asyncio
    async def test_work_on_issue_precommit_fails_max_attempts(self, temp_dir: Path) -> None:
        """Should fail when pre-commit fails and max attempts reached."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            max_fix_attempts=1,
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

        issue = Issue(1, "[Test] Issue", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue, fix_attempts=1)  # Already at max
        workflow.issues[1] = workflow_issue

        async def mock_impl(_issue: Issue) -> None:
            pass

        with (
            patch("specinit.github.workflow.create_branch"),
            patch("subprocess.run") as mock_run,
        ):
            # Pre-commit fails
            mock_run.return_value = MagicMock(returncode=1, stdout="fail", stderr="")
            await workflow.work_on_issue(workflow_issue, mock_impl)

        assert workflow_issue.status == IssueStatus.FAILED


class TestCoverageThresholds:
    """Tests for CoverageThresholds dataclass."""

    def test_default_values(self) -> None:
        """Should have correct default coverage thresholds."""
        thresholds = CoverageThresholds()

        assert thresholds.overall == 90
        assert thresholds.logic == 90
        assert thresholds.ui == 60
        assert thresholds.tests == 0

    def test_custom_values(self) -> None:
        """Should accept custom coverage thresholds."""
        thresholds = CoverageThresholds(overall=85, logic=95, ui=50, tests=0)

        assert thresholds.overall == 85
        assert thresholds.logic == 95
        assert thresholds.ui == 50


class TestGitHubConfigIterationSettings:
    """Tests for GitHubConfig iteration settings."""

    def test_default_iteration_settings(self) -> None:
        """Should have iteration enabled by default."""
        config = GitHubConfig(owner="test", repo="test")

        assert config.iterate_on_precommit is True
        assert config.iterate_on_ci is True
        assert config.iterate_on_coverage is True
        assert config.claude_code_review is False  # Off by default
        assert config.ci_timeout_seconds == 600
        assert config.review_poll_interval == 30

    def test_yolo_mode_with_claude_code_review(self) -> None:
        """Should allow enabling Claude Code review in YOLO mode."""
        config = GitHubConfig(
            owner="test",
            repo="test",
            yolo_mode=True,
            claude_code_review=True,
        )

        assert config.yolo_mode is True
        assert config.claude_code_review is True

    def test_custom_coverage_thresholds(self) -> None:
        """Should accept custom coverage thresholds in config."""
        thresholds = CoverageThresholds(overall=80, logic=85, ui=40)
        config = GitHubConfig(
            owner="test",
            repo="test",
            coverage_thresholds=thresholds,
        )

        assert config.coverage_thresholds.overall == 80
        assert config.coverage_thresholds.logic == 85
        assert config.coverage_thresholds.ui == 40


class TestIteratePrecommit:
    """Tests for _iterate_precommit method."""

    @pytest.fixture
    def workflow_for_iteration(self, temp_dir: Path) -> GitHubWorkflow:
        """Create workflow configured for iteration testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_precommit=True,
            max_fix_attempts=3,
        )
        service = MagicMock()
        return GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

    @pytest.mark.asyncio
    async def test_iterate_precommit_success_first_try(
        self, workflow_for_iteration: GitHubWorkflow
    ) -> None:
        """Should return True when pre-commit succeeds on first try."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        async def mock_impl(_issue: Issue) -> None:
            pass

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = await workflow_for_iteration._iterate_precommit(workflow_issue, mock_impl)

        assert result is True

    @pytest.mark.asyncio
    async def test_iterate_precommit_success_after_retry(
        self, workflow_for_iteration: GitHubWorkflow
    ) -> None:
        """Should retry and succeed after initial failure."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        call_count = 0

        async def mock_impl(_issue: Issue) -> None:
            pass

        def mock_subprocess(*_args: Any, **_kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            # First call fails, second succeeds
            if call_count == 1:
                return MagicMock(returncode=1, stdout="lint error", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=mock_subprocess):
            result = await workflow_for_iteration._iterate_precommit(workflow_issue, mock_impl)

        assert result is True

    @pytest.mark.asyncio
    async def test_iterate_precommit_fails_max_attempts(
        self, workflow_for_iteration: GitHubWorkflow
    ) -> None:
        """Should fail after max attempts exceeded."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        async def mock_impl(_issue: Issue) -> None:
            pass

        with patch("subprocess.run") as mock_run:
            # Always fail
            mock_run.return_value = MagicMock(returncode=1, stdout="error", stderr="")
            result = await workflow_for_iteration._iterate_precommit(workflow_issue, mock_impl)

        assert result is False
        assert workflow_issue.status == IssueStatus.PRECOMMIT_FAILED

    @pytest.mark.asyncio
    async def test_iterate_precommit_disabled(self, temp_dir: Path) -> None:
        """Should run once without iteration when disabled."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_precommit=False,
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        async def mock_impl(_issue: Issue) -> None:
            pass

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="error", stderr="")
            result = await workflow._iterate_precommit(workflow_issue, mock_impl)

        assert result is False
        # Should only call run once (no retry)
        assert mock_run.call_count == 1


class TestIterateCI:
    """Tests for _iterate_ci method."""

    @pytest.fixture
    def workflow_for_ci_iteration(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow configured for CI iteration testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_ci=True,
            iterate_on_coverage=True,
            max_fix_attempts=3,
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_iterate_ci_success_first_try(
        self, workflow_for_ci_iteration: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should return True when CI succeeds on first try."""
        workflow, service = workflow_for_ci_iteration
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "success"}]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        result = await workflow._iterate_ci(workflow_issue, mock_impl)

        assert result is True
        assert workflow_issue.status == IssueStatus.IN_REVIEW

    @pytest.mark.asyncio
    async def test_iterate_ci_fails_max_attempts(
        self, workflow_for_ci_iteration: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should fail after max CI fix attempts."""
        workflow, service = workflow_for_ci_iteration
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "failure"}]
        }
        service.get_workflow_run_logs.return_value = "Test failure logs"

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("specinit.github.workflow.push_branch"):
                result = await workflow._iterate_ci(workflow_issue, mock_impl)

        assert result is False


class TestCheckCoverage:
    """Tests for _check_coverage method."""

    @pytest.fixture
    def workflow_for_coverage(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow for coverage testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_coverage=True,
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_coverage_passes(
        self, workflow_for_coverage: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should return True when coverage check passes."""
        workflow, service = workflow_for_coverage
        service.get_pr_checks.return_value = {
            "check_runs": [
                {"name": "codecov/project", "status": "completed", "conclusion": "success"}
            ]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        result = await workflow._check_coverage(workflow_issue)

        assert result is True

    @pytest.mark.asyncio
    async def test_coverage_fails(
        self, workflow_for_coverage: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should return False when coverage check fails."""
        workflow, service = workflow_for_coverage
        service.get_pr_checks.return_value = {
            "check_runs": [
                {"name": "codecov/project", "status": "completed", "conclusion": "failure"}
            ]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        result = await workflow._check_coverage(workflow_issue)

        assert result is False
        assert workflow_issue.status == IssueStatus.COVERAGE_FAILED

    @pytest.mark.asyncio
    async def test_coverage_no_pr(
        self, workflow_for_coverage: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should return True when no PR exists."""
        workflow, _service = workflow_for_coverage

        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=None)

        result = await workflow._check_coverage(workflow_issue)

        assert result is True


class TestClaudeCodeReview:
    """Tests for Claude Code review detection."""

    @pytest.fixture
    def workflow_for_claude_review(self, temp_dir: Path) -> GitHubWorkflow:
        """Create workflow configured for Claude Code review testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            yolo_mode=True,
            claude_code_review=True,
        )
        service = MagicMock()
        return GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

    def test_check_claude_code_review_approved(
        self, workflow_for_claude_review: GitHubWorkflow
    ) -> None:
        """Should detect Claude Code approval."""
        reviews = [{"user": {"login": "claude-code[bot]"}, "state": "APPROVED", "body": "LGTM!"}]
        comments: list[dict[str, Any]] = []

        approved, feedback = workflow_for_claude_review._check_claude_code_review(reviews, comments)

        assert approved is True
        assert feedback == []

    def test_check_claude_code_review_changes_requested(
        self, workflow_for_claude_review: GitHubWorkflow
    ) -> None:
        """Should detect Claude Code change requests."""
        reviews = [
            {
                "user": {"login": "claude-code[bot]"},
                "state": "CHANGES_REQUESTED",
                "body": "Please fix the type error in line 42",
            }
        ]
        comments: list[dict[str, Any]] = []

        approved, feedback = workflow_for_claude_review._check_claude_code_review(reviews, comments)

        assert approved is False
        assert len(feedback) == 1
        assert "type error" in feedback[0]

    def test_check_claude_code_review_from_comments(
        self, workflow_for_claude_review: GitHubWorkflow
    ) -> None:
        """Should detect actionable feedback from Claude Code comments."""
        reviews: list[dict[str, Any]] = []
        comments = [
            {
                "user": {"login": "claude-code"},
                "body": "You should add error handling here",
            }
        ]

        approved, feedback = workflow_for_claude_review._check_claude_code_review(reviews, comments)

        assert approved is False
        assert len(feedback) == 1

    def test_is_actionable_feedback_true(self, workflow_for_claude_review: GitHubWorkflow) -> None:
        """Should identify actionable feedback."""
        actionable_comments = [
            "You should add error handling",
            "Consider refactoring this function",
            "This needs more tests",
            "There's a bug in the validation logic",
            "Please fix the typo",
        ]

        for comment in actionable_comments:
            assert workflow_for_claude_review._is_actionable_feedback(comment) is True

    def test_is_actionable_feedback_false(self, workflow_for_claude_review: GitHubWorkflow) -> None:
        """Should identify non-actionable feedback (approvals)."""
        approval_comments = [
            "LGTM!",
            "Looks good to me",
            "Approved!",
            "Ship it!",
            "Great work!",
        ]

        for comment in approval_comments:
            assert workflow_for_claude_review._is_actionable_feedback(comment) is False


class TestCommitAndPushFix:
    """Tests for _commit_and_push_fix method."""

    @pytest.fixture
    def workflow_for_commit(self, temp_dir: Path) -> GitHubWorkflow:
        """Create workflow for commit testing."""
        config = GitHubConfig(owner="testuser", repo="testrepo")
        service = MagicMock()
        return GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

    @pytest.mark.asyncio
    async def test_commit_and_push_with_changes(self, workflow_for_commit: GitHubWorkflow) -> None:
        """Should commit and push when there are changes."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue, branch_name="test-branch")

        with (
            patch("subprocess.run") as mock_run,
            patch("specinit.github.workflow.push_branch") as mock_push,
        ):
            # Simulate there are changes (diff --staged returns non-zero)
            mock_run.side_effect = [
                MagicMock(returncode=0),  # git add
                MagicMock(returncode=1),  # git diff --staged (changes exist)
                MagicMock(returncode=0),  # git commit
            ]

            await workflow_for_commit._commit_and_push_fix(workflow_issue, "fix: test")

        mock_push.assert_called_once_with("test-branch", force=False)

    @pytest.mark.asyncio
    async def test_commit_and_push_no_changes(self, workflow_for_commit: GitHubWorkflow) -> None:
        """Should skip commit when no changes."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue, branch_name="test-branch")

        with (
            patch("subprocess.run") as mock_run,
            patch("specinit.github.workflow.push_branch") as mock_push,
        ):
            # Simulate no changes (diff --staged returns zero)
            mock_run.side_effect = [
                MagicMock(returncode=0),  # git add
                MagicMock(returncode=0),  # git diff --staged (no changes)
            ]

            await workflow_for_commit._commit_and_push_fix(workflow_issue, "fix: test")

        mock_push.assert_not_called()


class TestIteratePrecommitWithCallback:
    """Additional tests for _iterate_precommit with progress callback."""

    @pytest.fixture
    def workflow_for_callback(self, temp_dir: Path) -> GitHubWorkflow:
        """Create workflow for callback testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_precommit=True,
            max_fix_attempts=2,
        )
        service = MagicMock()
        return GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

    @pytest.mark.asyncio
    async def test_iterate_precommit_calls_progress_callback(
        self, workflow_for_callback: GitHubWorkflow
    ) -> None:
        """Should call progress callback when fixing pre-commit failures."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        callback_calls: list[tuple] = []

        async def mock_callback(issue_id: str, status: str, data: dict | None) -> None:
            callback_calls.append((issue_id, status, data))

        call_count = 0

        async def mock_impl(_issue: Issue) -> None:
            pass

        def mock_subprocess(*_args: Any, **_kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            # First fails, second succeeds
            if call_count == 1:
                return MagicMock(returncode=1, stdout="error", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=mock_subprocess):
            await workflow_for_callback._iterate_precommit(workflow_issue, mock_impl, mock_callback)

        # Should have called callback for precommit_fixing
        assert any(c[1] == "precommit_fixing" for c in callback_calls)


class TestIterateCIWithCoverage:
    """Additional tests for _iterate_ci with coverage handling."""

    @pytest.fixture
    def workflow_for_ci_coverage(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow for CI + coverage testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_ci=True,
            iterate_on_coverage=True,
            max_fix_attempts=2,
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_iterate_ci_with_coverage_failure(
        self, workflow_for_ci_coverage: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should iterate when coverage fails."""
        workflow, service = workflow_for_ci_coverage

        call_count = 0

        def get_checks(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call (_wait_for_ci): All CI checks pass
                return {
                    "check_runs": [
                        {"status": "completed", "conclusion": "success", "name": "tests"},
                        {"status": "completed", "conclusion": "success", "name": "lint"},
                    ]
                }
            elif call_count == 2:
                # Second call (_check_coverage): Coverage check shows failure
                return {
                    "check_runs": [
                        {"status": "completed", "conclusion": "success", "name": "tests"},
                        {"status": "completed", "conclusion": "failure", "name": "codecov"},
                    ]
                }
            # Third+ calls: All pass
            return {
                "check_runs": [
                    {"status": "completed", "conclusion": "success", "name": "tests"},
                    {"status": "completed", "conclusion": "success", "name": "codecov"},
                ]
            }

        service.get_pr_checks.side_effect = get_checks

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        callback_calls: list[tuple] = []

        async def mock_callback(issue_id: str, status: str, data: dict | None) -> None:
            callback_calls.append((issue_id, status, data))

        with (
            patch("subprocess.run") as mock_run,
            patch("specinit.github.workflow.push_branch"),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            await workflow._iterate_ci(workflow_issue, mock_impl, mock_callback)

        # Should have called coverage_failed callback
        assert any(c[1] == "coverage_failed" for c in callback_calls)

    @pytest.mark.asyncio
    async def test_iterate_ci_without_iteration_enabled(self, temp_dir: Path) -> None:
        """Should not iterate when iterate_on_ci is False."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            iterate_on_ci=False,
            max_fix_attempts=2,
        )
        service = MagicMock()
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "failure"}]
        }
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        result = await workflow._iterate_ci(workflow_issue, mock_impl)

        assert result is False


class TestHandleReviewsAdvanced:
    """Additional tests for _handle_reviews method."""

    @pytest.fixture
    def workflow_for_reviews_advanced(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow for advanced review testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            yolo_mode=True,
            claude_code_review=True,
            max_fix_attempts=2,
            review_poll_interval=0,  # No wait for tests
        )
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_handle_reviews_with_changes_requested(
        self, workflow_for_reviews_advanced: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should handle changes requested and iterate."""
        workflow, service = workflow_for_reviews_advanced

        call_count = 0

        def get_reviews(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [{"state": "CHANGES_REQUESTED", "user": {"login": "reviewer"}}]
            return [{"state": "APPROVED", "user": {"login": "reviewer"}}]

        service.get_pr_reviews.side_effect = get_reviews
        service.get_pr_comments.return_value = []
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "success"}]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        with (
            patch("subprocess.run") as mock_run,
            patch("specinit.github.workflow.push_branch"),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            await workflow._handle_reviews(workflow_issue, mock_impl)

        assert workflow_issue.status == IssueStatus.APPROVED

    @pytest.mark.asyncio
    async def test_handle_reviews_with_claude_code_feedback(
        self, workflow_for_reviews_advanced: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should handle Claude Code review feedback."""
        workflow, service = workflow_for_reviews_advanced

        call_count = 0

        def get_reviews(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return [
                    {
                        "state": "CHANGES_REQUESTED",
                        "user": {"login": "claude-code[bot]"},
                        "body": "Please fix the type error",
                    }
                ]
            return [{"state": "APPROVED", "user": {"login": "claude-code[bot]"}}]

        service.get_pr_reviews.side_effect = get_reviews
        service.get_pr_comments.return_value = []
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "success"}]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        async def mock_impl(_issue: Issue) -> None:
            pass

        with (
            patch("subprocess.run") as mock_run,
            patch("specinit.github.workflow.push_branch"),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            await workflow._handle_reviews(workflow_issue, mock_impl)

        assert workflow_issue.status == IssueStatus.APPROVED


class TestClaudeCodeReviewAdvanced:
    """Additional tests for Claude Code review edge cases."""

    @pytest.fixture
    def workflow_for_claude(self, temp_dir: Path) -> GitHubWorkflow:
        """Create workflow for Claude review testing."""
        config = GitHubConfig(
            owner="testuser",
            repo="testrepo",
            yolo_mode=True,
            claude_code_review=True,
        )
        service = MagicMock()
        return GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)

    def test_claude_review_no_interaction(self, workflow_for_claude: GitHubWorkflow) -> None:
        """Should assume approved if no Claude interaction."""
        reviews: list[dict[str, Any]] = []
        comments: list[dict[str, Any]] = []

        approved, feedback = workflow_for_claude._check_claude_code_review(reviews, comments)

        # No interaction = consider approved
        assert approved is True
        assert feedback == []

    def test_claude_review_non_actionable_comment(
        self, workflow_for_claude: GitHubWorkflow
    ) -> None:
        """Should ignore non-actionable Claude comments."""
        reviews: list[dict[str, Any]] = []
        comments = [
            {
                "user": {"login": "claude-code[bot]"},
                "body": "LGTM! Great work!",  # Approval, not actionable
            }
        ]

        approved, feedback = workflow_for_claude._check_claude_code_review(reviews, comments)

        # LGTM comment should not add to feedback
        assert approved is True  # No explicit approval but no actionable feedback
        assert feedback == []

    def test_is_actionable_with_mixed_signals(self, workflow_for_claude: GitHubWorkflow) -> None:
        """Should prioritize approval indicators."""
        # Contains both action and approval words - approval wins
        comment = "Looks good but you might consider a small improvement"
        assert workflow_for_claude._is_actionable_feedback(comment) is False


class TestWaitForCIEdgeCases:
    """Test edge cases in _wait_for_ci."""

    @pytest.fixture
    def workflow_for_ci_wait(self, temp_dir: Path) -> tuple[GitHubWorkflow, MagicMock]:
        """Create workflow for CI wait testing."""
        config = GitHubConfig(owner="testuser", repo="testrepo", ci_timeout_seconds=1)
        service = MagicMock()
        workflow = GitHubWorkflow(config=config, project_path=temp_dir, github_service=service)
        return workflow, service

    @pytest.mark.asyncio
    async def test_wait_for_ci_no_check_runs(
        self, workflow_for_ci_wait: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should wait and eventually timeout with no check runs."""
        workflow, service = workflow_for_ci_wait
        # Return empty check runs repeatedly
        service.get_pr_checks.return_value = {"check_runs": []}

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        # Patch asyncio.sleep to speed up the test
        with patch("asyncio.sleep", return_value=None):
            await workflow._wait_for_ci(workflow_issue)

        # Should timeout and set CI_FAILED
        assert workflow_issue.status == IssueStatus.CI_FAILED

    @pytest.mark.asyncio
    async def test_wait_for_ci_skipped_checks(
        self, workflow_for_ci_wait: tuple[GitHubWorkflow, MagicMock]
    ) -> None:
        """Should pass when checks are skipped."""
        workflow, service = workflow_for_ci_wait
        service.get_pr_checks.return_value = {
            "check_runs": [{"status": "completed", "conclusion": "skipped"}]
        }

        issue = Issue(1, "Test", "", [], "open", "")
        pr = PullRequest(1, "PR", "", "branch", "main", "open", "")
        workflow_issue = WorkflowIssue(issue=issue, pr=pr, branch_name="branch")

        await workflow._wait_for_ci(workflow_issue)

        assert workflow_issue.status == IssueStatus.IN_REVIEW
