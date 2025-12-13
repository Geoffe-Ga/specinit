"""Tests for GitHub integration."""

from unittest.mock import MagicMock, patch

import pytest

from specinit.github.service import GitHubService


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
