"""Tests for GitHub service."""

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

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


class TestContentTypeValidation:
    """Tests for HTTP Content-Type validation (Issue #14 fix)."""

    def test_non_json_response_raises_error(self):
        """Non-JSON response should raise appropriate error."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.text = "<html>Error page</html>"
            mock_response.raise_for_status = MagicMock()
            mock_session.get.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")

            with pytest.raises(ValueError, match="Expected JSON response"):
                service.validate_token()

    def test_json_content_type_with_charset_accepted(self):
        """JSON Content-Type with charset should be accepted."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json; charset=utf-8"}
            mock_response.json.return_value = {"login": "testuser"}
            mock_response.raise_for_status = MagicMock()
            mock_session.get.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")
            result = service.validate_token()

            assert result["login"] == "testuser"

    def test_missing_content_type_raises_error(self):
        """Missing Content-Type header should raise appropriate error."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = "some response"
            mock_response.raise_for_status = MagicMock()
            mock_session.get.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")

            with pytest.raises(ValueError, match="Expected JSON response"):
                service.validate_token()


class TestAPIErrorDetails:
    """Tests for API exception handling with response details (Issue #16 fix)."""

    def test_api_error_includes_response_body(self):
        """API errors should include response body in exception message."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = '{"message": "Bad credentials"}'
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.raise_for_status.side_effect = HTTPError("401 Client Error: Unauthorized")
            mock_session.get.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="invalid-token")

            with pytest.raises(HTTPError) as exc_info:
                service.validate_token()

            # The error message should contain response details
            assert "Bad credentials" in str(exc_info.value)

    def test_create_issue_error_includes_response_body(self):
        """Issue creation errors should include response body details."""
        with patch("specinit.github.service.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.text = '{"message": "Validation Failed", "errors": [{"field": "title"}]}'
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.raise_for_status.side_effect = HTTPError(
                "422 Client Error: Unprocessable Entity"
            )
            mock_session.post.return_value = mock_response
            mock_session_cls.return_value = mock_session

            service = GitHubService(token="test-token")

            with pytest.raises(HTTPError) as exc_info:
                service.create_issue("owner", "repo", "Title", "Body")

            # Error should mention the validation failure
            assert "Validation Failed" in str(exc_info.value)
