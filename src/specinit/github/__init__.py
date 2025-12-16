"""GitHub integration module for SpecInit."""

from specinit.github.service import GitHubService
from specinit.github.workflow import CoverageThresholds, GitHubConfig, GitHubWorkflow

__all__ = ["CoverageThresholds", "GitHubConfig", "GitHubService", "GitHubWorkflow"]
