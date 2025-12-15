"""Tests for project history management."""

from pathlib import Path
from unittest.mock import patch

import pytest

from specinit.storage.history import HistoryManager


class TestHistoryManager:
    """Tests for HistoryManager."""

    @pytest.fixture(autouse=True)
    def setup_history_paths(self, mock_home: Path):
        """Set up mock paths for history database."""
        history_dir = mock_home / ".specinit"
        history_db = history_dir / "history.db"

        with (
            patch("specinit.storage.history.HISTORY_DIR", history_dir),
            patch("specinit.storage.history.HISTORY_DB", history_db),
        ):
            yield

    def test_ensure_db_creates_directory_and_schema(self, mock_home: Path):
        """Database directory and schema should be created on init."""
        manager = HistoryManager()

        # Directory should exist
        history_dir = mock_home / ".specinit"
        assert history_dir.exists()

        # Database file should exist
        history_db = history_dir / "history.db"
        assert history_db.exists()

        # Should be able to query the projects table
        projects = manager.get_recent()
        assert projects == []

    def test_add_project_with_all_parameters(self):
        """Should add a project with all parameters."""
        manager = HistoryManager()

        project_id = manager.add_project(
            name="test-project",
            path="/path/to/project",
            template="react-fastapi",
            platforms=["web", "mobile"],
            tech_stack=["React", "FastAPI"],
            cost=1.50,
            generation_time=45.5,
            status="completed",
        )

        assert project_id > 0

        # Verify the project was added
        project = manager.get_by_name("test-project")
        assert project is not None
        assert project["name"] == "test-project"
        assert project["path"] == "/path/to/project"
        assert project["template"] == "react-fastapi"
        assert project["platforms"] == "web,mobile"
        assert project["tech_stack"] == "React,FastAPI"
        assert project["cost"] == 1.50
        assert project["generation_time_seconds"] == 45.5
        assert project["status"] == "completed"

    def test_add_project_with_minimal_parameters(self):
        """Should add a project with only required parameters."""
        manager = HistoryManager()

        project_id = manager.add_project(
            name="minimal-project",
            path="/path/to/minimal",
        )

        assert project_id > 0

        project = manager.get_by_name("minimal-project")
        assert project is not None
        assert project["name"] == "minimal-project"
        assert project["cost"] == 0.0
        assert project["status"] == "completed"

    def test_update_project_with_valid_fields(self):
        """Should update project with allowed fields."""
        manager = HistoryManager()

        project_id = manager.add_project(
            name="update-test",
            path="/path/to/update",
            cost=0.0,
            status="in_progress",
        )

        manager.update_project(
            project_id,
            cost=2.50,
            generation_time_seconds=60.0,
            status="completed",
        )

        project = manager.get_by_name("update-test")
        assert project["cost"] == 2.50
        assert project["generation_time_seconds"] == 60.0
        assert project["status"] == "completed"

    def test_update_project_ignores_invalid_fields(self):
        """Should ignore fields not in allowed_fields."""
        manager = HistoryManager()

        project_id = manager.add_project(
            name="ignore-test",
            path="/path/to/ignore",
        )

        # Try to update with invalid field
        manager.update_project(
            project_id,
            name="hacked-name",  # Not in allowed_fields
            invalid_field="value",  # Not in allowed_fields
        )

        # Name should not have changed
        project = manager.get_by_name("ignore-test")
        assert project["name"] == "ignore-test"

    def test_update_project_with_empty_updates(self):
        """Should handle empty updates gracefully."""
        manager = HistoryManager()

        project_id = manager.add_project(
            name="empty-update-test",
            path="/path/to/empty",
        )

        # Should not raise
        manager.update_project(project_id)

    def test_get_recent_returns_projects_in_order(self):
        """Should return projects in descending order by created_at."""
        manager = HistoryManager()

        # Add multiple projects
        manager.add_project(name="first", path="/path/first")
        manager.add_project(name="second", path="/path/second")
        manager.add_project(name="third", path="/path/third")

        projects = manager.get_recent(limit=10)
        assert len(projects) == 3
        # Most recent first
        assert projects[0]["name"] == "third"
        assert projects[1]["name"] == "second"
        assert projects[2]["name"] == "first"

    def test_get_recent_respects_limit(self):
        """Should respect the limit parameter."""
        manager = HistoryManager()

        # Add 5 projects
        for i in range(5):
            manager.add_project(name=f"project-{i}", path=f"/path/{i}")

        projects = manager.get_recent(limit=3)
        assert len(projects) == 3

    def test_get_by_name_returns_project_when_found(self):
        """Should return project dict when found."""
        manager = HistoryManager()

        manager.add_project(name="findme", path="/path/findme")

        project = manager.get_by_name("findme")
        assert project is not None
        assert project["name"] == "findme"

    def test_get_by_name_returns_none_when_not_found(self):
        """Should return None when project not found."""
        manager = HistoryManager()

        project = manager.get_by_name("nonexistent")
        assert project is None

    def test_get_by_name_returns_most_recent(self):
        """Should return the most recent project with that name."""
        manager = HistoryManager()

        # Add same name twice with different paths
        manager.add_project(name="duplicate", path="/path/first")
        manager.add_project(name="duplicate", path="/path/second")

        project = manager.get_by_name("duplicate")
        assert project is not None
        assert project["path"] == "/path/second"  # Most recent

    def test_get_total_cost_with_projects(self):
        """Should return sum of all project costs."""
        manager = HistoryManager()

        manager.add_project(name="p1", path="/p1", cost=1.50)
        manager.add_project(name="p2", path="/p2", cost=2.25)
        manager.add_project(name="p3", path="/p3", cost=0.75)

        total = manager.get_total_cost()
        assert total == 4.50

    def test_get_total_cost_with_no_projects(self):
        """Should return 0.0 when no projects exist."""
        manager = HistoryManager()

        total = manager.get_total_cost()
        assert total == 0.0

    def test_get_project_count_with_projects(self):
        """Should return correct count of projects."""
        manager = HistoryManager()

        manager.add_project(name="p1", path="/p1")
        manager.add_project(name="p2", path="/p2")
        manager.add_project(name="p3", path="/p3")

        count = manager.get_project_count()
        assert count == 3

    def test_get_project_count_with_no_projects(self):
        """Should return 0 when no projects exist."""
        manager = HistoryManager()

        count = manager.get_project_count()
        assert count == 0
