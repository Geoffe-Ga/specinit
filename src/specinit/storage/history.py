"""Project history management using SQLite."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HISTORY_DIR = Path.home() / ".specinit"
HISTORY_DB = HISTORY_DIR / "history.db"


class HistoryManager:
    """Manages project generation history in SQLite."""

    def __init__(self) -> None:
        """Initialize the history manager."""
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Ensure the database exists with the correct schema."""
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(HISTORY_DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    template TEXT,
                    platforms TEXT,
                    tech_stack TEXT,
                    cost REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    generation_time_seconds REAL,
                    status TEXT DEFAULT 'completed'
                )
            """
            )
            conn.commit()

    def add_project(
        self,
        name: str,
        path: str,
        template: str | None = None,
        platforms: list[str] | None = None,
        tech_stack: list[str] | None = None,
        cost: float = 0.0,
        generation_time: float | None = None,
        status: str = "completed",
    ) -> int:
        """Add a project to the history."""
        with sqlite3.connect(HISTORY_DB) as conn:
            cursor = conn.execute(
                """
                INSERT INTO projects
                (name, path, template, platforms, tech_stack, cost, created_at,
                 generation_time_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    path,
                    template,
                    ",".join(platforms or []),
                    ",".join(tech_stack or []),
                    cost,
                    datetime.now(UTC).isoformat(),
                    generation_time,
                    status,
                ),
            )
            conn.commit()
            # lastrowid is only None for non-INSERT statements
            assert cursor.lastrowid is not None
            return cursor.lastrowid

    def update_project(self, project_id: int, **kwargs: Any) -> None:
        """Update a project record."""
        allowed_fields = {"cost", "generation_time_seconds", "status"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [project_id]

        with sqlite3.connect(HISTORY_DB) as conn:
            conn.execute(
                f"UPDATE projects SET {set_clause} WHERE id = ?",
                values,
            )
            conn.commit()

    def get_recent(self, limit: int = 10) -> list[dict]:
        """Get recent projects."""
        with sqlite3.connect(HISTORY_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM projects
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_by_name(self, name: str) -> dict | None:
        """Get a project by name."""
        with sqlite3.connect(HISTORY_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM projects WHERE name = ? ORDER BY created_at DESC LIMIT 1",
                (name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_total_cost(self) -> float:
        """Get total cost across all projects."""
        with sqlite3.connect(HISTORY_DB) as conn:
            cursor = conn.execute("SELECT SUM(cost) FROM projects")
            result = cursor.fetchone()[0]
            return result or 0.0

    def get_project_count(self) -> int:
        """Get total number of projects generated."""
        with sqlite3.connect(HISTORY_DB) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM projects")
            return cursor.fetchone()[0]
