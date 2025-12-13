"""Tests for GitHub workflow orchestration."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

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
    def mock_github_service(self):
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
        service.get_pr_reviews.return_value = [
            {"state": "APPROVED"}
        ]
        service.get_pr_comments.return_value = []
        service.merge_pull_request.return_value = True
        return service

    @pytest.fixture
    def github_config(self):
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
    def workflow(self, github_config, mock_github_service, temp_dir):
        """Create a test workflow."""
        return GitHubWorkflow(
            config=github_config,
            project_path=temp_dir,
            github_service=mock_github_service,
        )

    @pytest.mark.asyncio
    async def test_setup_repository_creates_labels(self, workflow, mock_github_service):
        """Should create labels when setting up repository."""
        await workflow.setup_repository()

        # Should create multiple labels
        assert mock_github_service.create_label.call_count >= 5

    @pytest.mark.asyncio
    async def test_create_milestone(self, workflow, mock_github_service):
        """Should create a milestone."""
        milestone_number = await workflow.create_milestone("v1.0.0", "Initial release")

        assert milestone_number == 1
        mock_github_service.create_milestone.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_issues_from_spec(self, workflow, mock_github_service):
        """Should create issues based on spec."""
        issues = await workflow.create_issues_from_spec(
            spec_content="Test spec",
            features=["Feature 1", "Feature 2"],
            user_story={"role": "user", "action": "test", "outcome": "result"},
        )

        # Should create setup issues + feature issues + test issue
        # 4 setup + 2 features + 1 test = 7 issues
        assert len(issues) >= 5

    def test_get_ready_issues_no_dependencies(self, workflow):
        """Should return issues with no dependencies."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(issue=issue1, dependencies=[])
        workflow.issues[2] = WorkflowIssue(issue=issue2, dependencies=[])

        ready = workflow.get_ready_issues()

        assert len(ready) == 2

    def test_get_ready_issues_with_dependencies(self, workflow):
        """Should not return issues with unmet dependencies."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(
            issue=issue1, dependencies=[], status=IssueStatus.QUEUED
        )
        workflow.issues[2] = WorkflowIssue(
            issue=issue2, dependencies=[1], status=IssueStatus.QUEUED
        )

        ready = workflow.get_ready_issues()

        # Only issue 1 should be ready (issue 2 depends on 1)
        assert len(ready) == 1
        assert ready[0].issue.number == 1

    def test_get_ready_issues_after_merge(self, workflow):
        """Should return dependent issues after dependency is merged."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(
            issue=issue1, dependencies=[], status=IssueStatus.MERGED
        )
        workflow.issues[2] = WorkflowIssue(
            issue=issue2, dependencies=[1], status=IssueStatus.QUEUED
        )

        ready = workflow.get_ready_issues()

        # Issue 2 should now be ready since issue 1 is merged
        assert len(ready) == 1
        assert ready[0].issue.number == 2

    def test_get_status_summary(self, workflow):
        """Should return correct status summary."""
        issue1 = Issue(1, "Issue 1", "", [], "open", "")
        issue2 = Issue(2, "Issue 2", "", [], "open", "")
        issue3 = Issue(3, "Issue 3", "", [], "open", "")

        workflow.issues[1] = WorkflowIssue(
            issue=issue1, status=IssueStatus.MERGED
        )
        workflow.issues[2] = WorkflowIssue(
            issue=issue2, status=IssueStatus.IN_PROGRESS
        )
        workflow.issues[3] = WorkflowIssue(
            issue=issue3, status=IssueStatus.QUEUED
        )

        summary = workflow.get_status_summary()

        assert summary["total_issues"] == 3
        assert summary["merged"] == 1
        assert summary["in_progress"] == 1

    def test_slugify(self, workflow):
        """Should create URL-safe slugs."""
        assert workflow._slugify("[Setup] Initialize project") == "setup-initialize-project"
        assert workflow._slugify("[Feature] Add dark mode!") == "feature-add-dark-mode"
        assert workflow._slugify("Test   Multiple   Spaces") == "test-multiple-spaces"

    @pytest.mark.asyncio
    async def test_work_on_issue_creates_branch_and_pr(
        self, workflow, mock_github_service, temp_dir
    ):
        """Should create branch and PR when working on issue."""
        issue = Issue(1, "[Setup] Test Issue", "Body", ["specinit"], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)
        workflow.issues[1] = workflow_issue

        async def mock_implementation(i):
            # Create a test file
            (temp_dir / "test.txt").write_text("test content")

        with patch("specinit.github.workflow.create_branch"):
            with patch("specinit.github.workflow.push_branch"):
                with patch("subprocess.run"):
                    await workflow.work_on_issue(
                        workflow_issue, mock_implementation
                    )

        # Should have created a PR
        mock_github_service.create_pull_request.assert_called()


class TestIssueStatus:
    """Tests for IssueStatus enum."""

    def test_all_statuses_defined(self):
        """All expected statuses should be defined."""
        expected = [
            "queued", "in_progress", "pr_created", "ci_running",
            "ci_failed", "in_review", "changes_requested",
            "approved", "merged", "blocked", "failed"
        ]

        for status in expected:
            assert hasattr(IssueStatus, status.upper())


class TestWorkflowIssue:
    """Tests for WorkflowIssue dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        issue = Issue(1, "Test", "", [], "open", "")
        workflow_issue = WorkflowIssue(issue=issue)

        assert workflow_issue.status == IssueStatus.QUEUED
        assert workflow_issue.branch_name == ""
        assert workflow_issue.pr is None
        assert workflow_issue.dependencies == []
        assert workflow_issue.fix_attempts == 0
        assert workflow_issue.error_message == ""
