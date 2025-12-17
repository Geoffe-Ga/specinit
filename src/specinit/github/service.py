"""GitHub API service for SpecInit."""

import contextlib
import re
import subprocess
from dataclasses import dataclass
from typing import Any, cast

import keyring
import requests

GITHUB_SERVICE = "specinit-github"
GITHUB_API_BASE = "https://api.github.com"


@dataclass
class Issue:
    """Represents a GitHub issue."""

    number: int
    title: str
    body: str
    labels: list[str]
    state: str = "open"
    url: str = ""


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""

    number: int
    title: str
    body: str
    head: str
    base: str
    state: str = "open"
    url: str = ""
    mergeable: bool | None = None
    ci_status: str | None = None


class GitHubService:
    """Service for interacting with GitHub API."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize the GitHub service."""
        self.token = token or self.get_token()
        self.session = requests.Session()
        if self.token:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
            )

    def close(self) -> None:
        """Close the session and release resources.

        Issue #9 Fix: Properly close the requests session to prevent resource leaks.
        """
        if self.session:
            self.session.close()

    def __enter__(self) -> "GitHubService":
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager and close session."""
        self.close()

    def _validate_json_response(self, response: requests.Response) -> None:
        """Validate that response has JSON Content-Type.

        Issue #14 Fix: Verify Content-Type before parsing JSON to avoid
        unexpected errors when server returns non-JSON responses.

        Raises:
            ValueError: If response is not JSON content type.
        """
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("application/json"):
            raise ValueError(
                f"Expected JSON response but got Content-Type: {content_type!r}. "
                f"Response body: {response.text[:500]}"
            )

    def _raise_for_status_with_details(self, response: requests.Response) -> None:
        """Raise HTTPError with response body details if request failed.

        Issue #16 Fix: Include response body in exception message for
        easier debugging of API errors.
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Enhance error message with response details
            error_details = response.text[:1000] if response.text else "No response body"
            raise requests.exceptions.HTTPError(
                f"{e}. Response details: {error_details}",
                response=response,
            ) from e

    @staticmethod
    def get_token() -> str | None:
        """Get GitHub token from keyring."""
        try:
            return keyring.get_password(GITHUB_SERVICE, "token")
        except Exception:
            return None

    @staticmethod
    def set_token(token: str) -> None:
        """Store GitHub token securely."""
        keyring.set_password(GITHUB_SERVICE, "token", token)

    @staticmethod
    def delete_token() -> None:
        """Remove GitHub token from keyring."""
        with contextlib.suppress(Exception):
            keyring.delete_password(GITHUB_SERVICE, "token")

    def validate_token(self) -> dict[str, Any]:
        """Validate the token and return user info."""
        if not self.token:
            raise ValueError("No GitHub token configured")

        response = self.session.get(f"{GITHUB_API_BASE}/user")
        self._raise_for_status_with_details(response)
        self._validate_json_response(response)
        return cast(dict[str, Any], response.json())

    @staticmethod
    def parse_repo_url(url: str) -> tuple[str, str]:
        """Parse owner and repo from GitHub URL."""
        # Handle various URL formats
        patterns = [
            r"github\.com[:/]([^/]+)/([^/\.]+)",  # HTTPS or SSH
            r"^([^/]+)/([^/]+)$",  # owner/repo format
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2).replace(".git", "")

        raise ValueError(f"Invalid GitHub URL: {url}")

    def repo_exists(self, owner: str, repo: str) -> bool:
        """Check if a repository exists."""
        response = self.session.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")
        return response.status_code == 200

    def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = True,
        auto_init: bool = False,
    ) -> dict[str, Any]:
        """Create a new repository."""
        response = self.session.post(
            f"{GITHUB_API_BASE}/user/repos",
            json={
                "name": name,
                "description": description,
                "private": private,
                "auto_init": auto_init,
            },
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
        milestone: int | None = None,
    ) -> Issue:
        """Create a new issue."""
        data: dict[str, Any] = {"title": title, "body": body}
        if labels:
            data["labels"] = labels
        if milestone:
            data["milestone"] = milestone

        response = self.session.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
            json=data,
        )
        self._raise_for_status_with_details(response)
        result = response.json()

        return Issue(
            number=result["number"],
            title=result["title"],
            body=result["body"],
            labels=[label["name"] for label in result.get("labels", [])],
            state=result["state"],
            url=result["html_url"],
        )

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: str | None = None,
    ) -> list[Issue]:
        """Get issues from a repository."""
        params: dict[str, Any] = {"state": state}
        if labels:
            params["labels"] = labels

        response = self.session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
            params=params,
        )
        response.raise_for_status()

        return [
            Issue(
                number=i["number"],
                title=i["title"],
                body=i["body"] or "",
                labels=[label["name"] for label in i.get("labels", [])],
                state=i["state"],
                url=i["html_url"],
            )
            for i in response.json()
            if "pull_request" not in i  # Exclude PRs
        ]

    def close_issue(self, owner: str, repo: str, issue_number: int) -> None:
        """Close an issue."""
        response = self.session.patch(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}",
            json={"state": "closed"},
        )
        response.raise_for_status()

    def create_milestone(
        self,
        owner: str,
        repo: str,
        title: str,
        description: str = "",
    ) -> int:
        """Create a milestone and return its number."""
        response = self.session.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/milestones",
            json={"title": title, "description": description},
        )
        response.raise_for_status()
        result = response.json()["number"]
        assert isinstance(result, int)
        return result

    def create_label(
        self,
        owner: str,
        repo: str,
        name: str,
        color: str,
        description: str = "",
    ) -> None:
        """Create a label (ignores if already exists)."""
        response = self.session.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/labels",
            json={"name": name, "color": color, "description": description},
        )
        # Ignore 422 (already exists)
        if response.status_code not in (201, 422):
            response.raise_for_status()

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> PullRequest:
        """Create a pull request."""
        response = self.session.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls",
            json={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            },
        )
        response.raise_for_status()
        result = response.json()

        return PullRequest(
            number=result["number"],
            title=result["title"],
            body=result["body"] or "",
            head=result["head"]["ref"],
            base=result["base"]["ref"],
            state=result["state"],
            url=result["html_url"],
            mergeable=result.get("mergeable"),
        )

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> PullRequest:
        """Get a pull request."""
        response = self.session.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}")
        response.raise_for_status()
        result = response.json()

        return PullRequest(
            number=result["number"],
            title=result["title"],
            body=result["body"] or "",
            head=result["head"]["ref"],
            base=result["base"]["ref"],
            state=result["state"],
            url=result["html_url"],
            mergeable=result.get("mergeable"),
        )

    def get_pr_checks(self, owner: str, repo: str, ref: str) -> dict[str, Any]:
        """Get check runs for a ref."""
        response = self.session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits/{ref}/check-runs"
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def get_pr_reviews(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """Get reviews for a pull request."""
        response = self.session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        )
        response.raise_for_status()
        return cast(list[dict[str, Any]], response.json())

    def get_pr_comments(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """Get review comments for a pull request."""
        response = self.session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        )
        response.raise_for_status()
        return cast(list[dict[str, Any]], response.json())

    def merge_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        merge_method: str = "squash",
    ) -> bool:
        """Merge a pull request.

        Issue #17 Fix: Properly distinguish between different failure modes
        and raise appropriate exceptions.

        Returns:
            True if merge was successful.

        Raises:
            ValueError: If PR cannot be merged (405) or has conflicts (409).
            RuntimeError: For other API errors.
        """
        response = self.session.put(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/merge",
            json={"merge_method": merge_method},
        )

        if response.status_code == 200:
            return True
        elif response.status_code == 405:
            message = response.json().get("message", "Unknown reason")
            raise ValueError(f"PR cannot be merged: {message}")
        elif response.status_code == 409:
            raise ValueError("PR has merge conflicts that must be resolved first")
        else:
            raise RuntimeError(f"Merge failed with status {response.status_code}")

    def get_workflow_runs(
        self, owner: str, repo: str, branch: str | None = None
    ) -> list[dict[str, Any]]:
        """Get workflow runs for a repository."""
        params = {}
        if branch:
            params["branch"] = branch

        response = self.session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs",
            params=params,
        )
        response.raise_for_status()
        data = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], data.get("workflow_runs", []))

    def get_workflow_run_logs(self, owner: str, repo: str, run_id: int) -> str:
        """Get logs for a workflow run."""
        response = self.session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
            allow_redirects=True,
        )
        if response.status_code == 200:
            return response.text
        return ""


def setup_git_remote(repo_url: str, remote_name: str = "origin") -> None:
    """Set up git remote for a repository."""
    # Check if remote already exists
    result = subprocess.run(
        ["git", "remote", "get-url", remote_name],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        # Remote exists, update it
        subprocess.run(
            ["git", "remote", "set-url", remote_name, repo_url],
            check=True,
        )
    else:
        # Add new remote
        subprocess.run(
            ["git", "remote", "add", remote_name, repo_url],
            check=True,
        )


def create_branch(branch_name: str, base: str = "main") -> None:
    """Create and checkout a new branch."""
    subprocess.run(["git", "checkout", base], check=True, capture_output=True)
    subprocess.run(["git", "pull", "--rebase"], capture_output=True, check=False)
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)


def push_branch(branch_name: str, force: bool = False) -> None:
    """Push a branch to origin."""
    cmd = ["git", "push", "-u", "origin", branch_name]
    if force:
        cmd.insert(2, "--force")
    subprocess.run(cmd, check=True)
