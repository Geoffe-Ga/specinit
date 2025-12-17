"""Tests for GitHub service."""

from unittest.mock import MagicMock, patch

import pytest

from specinit.github.service import GitHubService


class TestGitHubServiceSession:
    """Tests for GitHubService session management (Issue #9 fix)."""

    def test_close_closes_session(self):
        """close() should close the underlying requests session."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")
            service.close()

            mock_session.close.assert_called_once()

    def test_context_manager_closes_session_on_exit(self):
        """Using as context manager should close session on exit."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            with GitHubService(token="test-token") as service:
                assert service is not None

            mock_session.close.assert_called_once()

    def test_context_manager_closes_session_on_exception(self):
        """Context manager should close session even when exception occurs."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            with pytest.raises(ValueError), GitHubService(token="test-token"):
                raise ValueError("Test error")

            mock_session.close.assert_called_once()

    def test_context_manager_returns_self(self):
        """Context manager __enter__ should return self."""
        with patch("specinit.github.service.requests.Session"):
            service = GitHubService(token="test-token")
            result = service.__enter__()
            assert result is service
            service.close()


class TestMergePullRequest:
    """Tests for merge_pull_request error handling (Issue #17 fix)."""

    def test_merge_success_returns_true(self):
        """Successful merge should return True."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_session.put.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")
            result = service.merge_pull_request("owner", "repo", 1)

            assert result is True

    def test_merge_not_allowed_raises_value_error(self):
        """405 status should raise ValueError with message."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 405
            mock_response.json.return_value = {"message": "Pull Request is not mergeable"}
            mock_session.put.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")

            with pytest.raises(ValueError, match="cannot be merged"):
                service.merge_pull_request("owner", "repo", 1)

    def test_merge_conflict_raises_value_error(self):
        """409 status should raise ValueError about merge conflicts."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 409
            mock_session.put.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")

            with pytest.raises(ValueError, match="merge conflicts"):
                service.merge_pull_request("owner", "repo", 1)

    def test_merge_other_error_raises_runtime_error(self):
        """Other error status should raise RuntimeError."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_session.put.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")

            with pytest.raises(RuntimeError, match="status 500"):
                service.merge_pull_request("owner", "repo", 1)


class TestParseRepoUrl:
    """Tests for parse_repo_url."""

    def test_parse_https_url(self):
        """Should parse HTTPS GitHub URLs."""
        owner, repo = GitHubService.parse_repo_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_ssh_url(self):
        """Should parse SSH GitHub URLs."""
        owner, repo = GitHubService.parse_repo_url("git@github.com:owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_owner_repo_format(self):
        """Should parse owner/repo format."""
        owner, repo = GitHubService.parse_repo_url("owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_invalid_url_raises(self):
        """Should raise ValueError for invalid URLs."""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            GitHubService.parse_repo_url("not-a-valid-url")
