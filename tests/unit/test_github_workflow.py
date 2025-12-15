"""Tests for GitHub workflow orchestration."""

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from specinit.github.service import Issue, PullRequest
from specinit.github.workflow import (
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
            patch("subprocess.run"),
        ):
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
            "pr_created",
            "ci_running",
            "ci_failed",
            "in_review",
            "changes_requested",
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
