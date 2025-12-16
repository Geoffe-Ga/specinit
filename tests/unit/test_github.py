"""Tests for GitHub integration."""

from unittest.mock import MagicMock, patch

import pytest

from specinit.github.service import (
    GitHubService,
    create_branch,
    push_branch,
    setup_git_remote,
)


class TestGitHubService:
    """Tests for GitHubService."""

    def test_parse_repo_url_https(self):
        """Should parse HTTPS GitHub URLs."""
        owner, repo = GitHubService.parse_repo_url("https://github.com/user/my-repo")
        assert owner == "user"
        assert repo == "my-repo"

    def test_parse_repo_url_https_with_git(self):
        """Should parse HTTPS URLs with .git suffix."""
        owner, repo = GitHubService.parse_repo_url("https://github.com/user/my-repo.git")
        assert owner == "user"
        assert repo == "my-repo"

    def test_parse_repo_url_ssh(self):
        """Should parse SSH GitHub URLs."""
        owner, repo = GitHubService.parse_repo_url("git@github.com:user/my-repo.git")
        assert owner == "user"
        assert repo == "my-repo"

    def test_parse_repo_url_short_form(self):
        """Should parse owner/repo format."""
        owner, repo = GitHubService.parse_repo_url("user/my-repo")
        assert owner == "user"
        assert repo == "my-repo"

    def test_parse_repo_url_invalid(self):
        """Should raise error for invalid URLs."""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            GitHubService.parse_repo_url("not-a-valid-url")

    @patch("specinit.github.service.requests.Session")
    def test_validate_token_success(self, mock_session_class):
        """Should validate a valid token."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"login": "testuser"}
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="ghp_test_token")
        user_info = github.validate_token()

        assert user_info["login"] == "testuser"

    @patch("specinit.github.service.keyring")
    def test_get_token_from_keyring(self, mock_keyring):
        """Should retrieve token from keyring."""
        mock_keyring.get_password.return_value = "stored_token"

        token = GitHubService.get_token()

        assert token == "stored_token"
        mock_keyring.get_password.assert_called_once_with("specinit-github", "token")

    @patch("specinit.github.service.keyring")
    def test_set_token_in_keyring(self, mock_keyring):
        """Should store token in keyring."""
        GitHubService.set_token("new_token")

        mock_keyring.set_password.assert_called_once_with("specinit-github", "token", "new_token")

    @patch("specinit.github.service.requests.Session")
    def test_create_issue(self, mock_session_class):
        """Should create a GitHub issue."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test Issue",
            "body": "Issue body",
            "labels": [{"name": "bug"}],
            "state": "open",
            "html_url": "https://github.com/user/repo/issues/1",
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        issue = github.create_issue(
            owner="user",
            repo="repo",
            title="Test Issue",
            body="Issue body",
            labels=["bug"],
        )

        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert "bug" in issue.labels

    @patch("specinit.github.service.requests.Session")
    def test_create_pull_request(self, mock_session_class):
        """Should create a pull request."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test PR",
            "body": "PR body",
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
            "state": "open",
            "html_url": "https://github.com/user/repo/pull/1",
            "mergeable": True,
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        pr = github.create_pull_request(
            owner="user",
            repo="repo",
            title="Test PR",
            body="PR body",
            head="feature-branch",
            base="main",
        )

        assert pr.number == 1
        assert pr.title == "Test PR"
        assert pr.head == "feature-branch"
        assert pr.base == "main"

    @patch("specinit.github.service.requests.Session")
    def test_get_pr_checks(self, mock_session_class):
        """Should get check runs for a PR."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "check_runs": [
                {"name": "test", "status": "completed", "conclusion": "success"},
                {"name": "lint", "status": "completed", "conclusion": "success"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        checks = github.get_pr_checks("user", "repo", "feature-branch")

        assert len(checks["check_runs"]) == 2
        assert all(c["status"] == "completed" for c in checks["check_runs"])

    @patch("specinit.github.service.requests.Session")
    def test_merge_pull_request(self, mock_session_class):
        """Should merge a pull request."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        success = github.merge_pull_request("user", "repo", 1)

        assert success is True

    @patch("specinit.github.service.requests.Session")
    def test_repo_exists_true(self, mock_session_class):
        """Should return True for existing repo."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        exists = github.repo_exists("user", "repo")

        assert exists is True

    @patch("specinit.github.service.requests.Session")
    def test_repo_exists_false(self, mock_session_class):
        """Should return False for non-existing repo."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        exists = github.repo_exists("user", "nonexistent")

        assert exists is False

    @patch("specinit.github.service.requests.Session")
    def test_create_repo(self, mock_session_class):
        """Should create a GitHub repository."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "new-repo",
            "full_name": "user/new-repo",
            "html_url": "https://github.com/user/new-repo",
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        result = github.create_repo(
            name="new-repo",
            description="A new repository",
            private=False,
            auto_init=True,
        )

        assert result["name"] == "new-repo"
        mock_session.post.assert_called_once()

    @patch("specinit.github.service.requests.Session")
    def test_create_milestone(self, mock_session_class):
        """Should create a milestone and return its number."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "v1.0.0",
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        milestone_number = github.create_milestone(
            owner="user",
            repo="repo",
            title="v1.0.0",
            description="First release",
        )

        assert milestone_number == 1

    @patch("specinit.github.service.requests.Session")
    def test_create_label(self, mock_session_class):
        """Should create a label."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201  # Created successfully
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        # Should not raise
        github.create_label(
            owner="user",
            repo="repo",
            name="bug",
            color="ff0000",
            description="Bug reports",
        )

        mock_session.post.assert_called_once()

    @patch("specinit.github.service.requests.Session")
    def test_create_label_already_exists(self, mock_session_class):
        """Should handle label already existing (422 status)."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 422  # Label already exists
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        # Should not raise - silently handles existing label (422)
        github.create_label(
            owner="user",
            repo="repo",
            name="existing-label",
            color="00ff00",
        )

    @patch("specinit.github.service.requests.Session")
    def test_get_pr_reviews(self, mock_session_class):
        """Should get reviews for a PR."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"state": "APPROVED", "user": {"login": "reviewer1"}},
            {"state": "CHANGES_REQUESTED", "user": {"login": "reviewer2"}},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        reviews = github.get_pr_reviews("user", "repo", 1)

        assert len(reviews) == 2
        assert reviews[0]["state"] == "APPROVED"

    @patch("specinit.github.service.requests.Session")
    def test_get_pr_comments(self, mock_session_class):
        """Should get review comments for a PR."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"body": "Please fix this", "user": {"login": "reviewer"}},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        comments = github.get_pr_comments("user", "repo", 1)

        assert len(comments) == 1
        assert "fix" in comments[0]["body"]

    @patch("specinit.github.service.requests.Session")
    def test_merge_pull_request_failure(self, mock_session_class):
        """Should raise ValueError when merge fails with 405.

        Issue #17 Fix: Now raises specific exceptions instead of returning False.
        """
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 405  # Not mergeable
        mock_response.json.return_value = {"message": "PR is not mergeable"}
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")

        with pytest.raises(ValueError, match="cannot be merged"):
            github.merge_pull_request("user", "repo", 1)

    @patch("specinit.github.service.requests.Session")
    def test_get_workflow_runs(self, mock_session_class):
        """Should get workflow runs for a repository."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "workflow_runs": [
                {"id": 1, "status": "completed", "conclusion": "success"},
                {"id": 2, "status": "in_progress"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        runs = github.get_workflow_runs("user", "repo")

        assert len(runs) == 2
        assert runs[0]["status"] == "completed"

    @patch("specinit.github.service.requests.Session")
    def test_get_workflow_runs_with_branch(self, mock_session_class):
        """Should filter workflow runs by branch."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"workflow_runs": []}
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        github.get_workflow_runs("user", "repo", branch="feature")

        # Verify branch was passed as param
        call_args = mock_session.get.call_args
        assert "params" in call_args.kwargs or call_args[1].get("params")

    @patch("specinit.github.service.requests.Session")
    def test_get_workflow_run_logs_success(self, mock_session_class):
        """Should get workflow run logs."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Log output here"
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        logs = github.get_workflow_run_logs("user", "repo", 123)

        assert logs == "Log output here"

    @patch("specinit.github.service.requests.Session")
    def test_get_workflow_run_logs_not_found(self, mock_session_class):
        """Should return empty string when logs not found."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        github = GitHubService(token="test_token")
        logs = github.get_workflow_run_logs("user", "repo", 999)

        assert logs == ""


class TestGitOperations:
    """Tests for git operations."""

    @patch("specinit.github.service.subprocess.run")
    def test_setup_git_remote_new(self, mock_run):
        """Should add new remote when it doesn't exist."""
        # First call returns non-zero (remote doesn't exist)
        mock_run.return_value = MagicMock(returncode=1)

        setup_git_remote("https://github.com/user/repo.git", "origin")

        # Should have called git remote add
        calls = mock_run.call_args_list
        assert len(calls) >= 2
        # Last call should be 'git remote add'
        add_call = [c for c in calls if "add" in str(c)]
        assert len(add_call) > 0

    @patch("specinit.github.service.subprocess.run")
    def test_setup_git_remote_update(self, mock_run):
        """Should update existing remote."""
        # First call returns zero (remote exists)
        mock_run.return_value = MagicMock(returncode=0)

        setup_git_remote("https://github.com/user/new-repo.git", "origin")

        # Should have called git remote set-url
        calls = mock_run.call_args_list
        set_url_call = [c for c in calls if "set-url" in str(c)]
        assert len(set_url_call) > 0

    @patch("specinit.github.service.subprocess.run")
    def test_create_branch(self, mock_run):
        """Should create and checkout a new branch."""
        mock_run.return_value = MagicMock(returncode=0)

        create_branch("feature-branch", "main")

        calls = mock_run.call_args_list
        # Should have checkout main, pull, and checkout -b
        assert len(calls) == 3

    @patch("specinit.github.service.subprocess.run")
    def test_push_branch(self, mock_run):
        """Should push branch to origin."""
        mock_run.return_value = MagicMock(returncode=0)

        push_branch("feature-branch")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "push" in call_args
        assert "-u" in call_args
        assert "feature-branch" in call_args

    @patch("specinit.github.service.subprocess.run")
    def test_push_branch_force(self, mock_run):
        """Should force push when specified."""
        mock_run.return_value = MagicMock(returncode=0)

        push_branch("feature-branch", force=True)

        call_args = mock_run.call_args[0][0]
        assert "--force" in call_args
