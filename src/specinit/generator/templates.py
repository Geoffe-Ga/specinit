"""Built-in project templates."""

from typing import Any

TEMPLATES = {
    "react-fastapi": {
        "name": "React + FastAPI Web App",
        "description": "Full-stack web application with React frontend and FastAPI backend",
        "platforms": ["web"],
        "tech_stack": {
            "frontend": ["react", "typescript", "vite", "tailwind"],
            "backend": ["fastapi", "python", "uvicorn"],
            "database": ["postgresql", "sqlalchemy"],
            "tools": ["pytest", "eslint", "prettier"],
        },
        "directory_structure": [
            "frontend/src/",
            "frontend/src/components/",
            "frontend/src/pages/",
            "frontend/src/hooks/",
            "frontend/src/utils/",
            "frontend/public/",
            "backend/app/",
            "backend/app/api/",
            "backend/app/models/",
            "backend/app/schemas/",
            "backend/tests/",
            "docs/",
            "plan/",
        ],
    },
    "react-native": {
        "name": "React Native Mobile App",
        "description": "Cross-platform mobile application for iOS and Android",
        "platforms": ["ios", "android"],
        "tech_stack": {
            "frontend": ["react-native", "typescript", "expo"],
            "backend": ["fastapi", "python"],
            "database": ["supabase"],
            "tools": ["jest", "eslint", "prettier"],
        },
        "directory_structure": [
            "src/",
            "src/components/",
            "src/screens/",
            "src/navigation/",
            "src/hooks/",
            "src/utils/",
            "src/api/",
            "__tests__/",
            "docs/",
            "plan/",
        ],
    },
    "nextjs": {
        "name": "Next.js Web App",
        "description": "Full-stack web application with Next.js and API routes",
        "platforms": ["web"],
        "tech_stack": {
            "frontend": ["nextjs", "react", "typescript", "tailwind"],
            "backend": ["nextjs-api"],
            "database": ["postgresql", "prisma"],
            "tools": ["jest", "eslint", "prettier"],
        },
        "directory_structure": [
            "src/app/",
            "src/components/",
            "src/lib/",
            "src/hooks/",
            "prisma/",
            "public/",
            "__tests__/",
            "docs/",
            "plan/",
        ],
    },
    "python-cli": {
        "name": "Python CLI Tool",
        "description": "Command-line tool built with Click",
        "platforms": ["cli"],
        "tech_stack": {
            "frontend": [],
            "backend": ["python", "click"],
            "database": ["sqlite"],
            "tools": ["pytest", "ruff", "mypy"],
        },
        "directory_structure": [
            "src/",
            "src/cli/",
            "src/core/",
            "src/utils/",
            "tests/",
            "tests/unit/",
            "tests/integration/",
            "docs/",
            "plan/",
        ],
    },
    "fastapi-only": {
        "name": "FastAPI Backend",
        "description": "API backend service with FastAPI",
        "platforms": ["api"],
        "tech_stack": {
            "frontend": [],
            "backend": ["fastapi", "python", "uvicorn"],
            "database": ["postgresql", "sqlalchemy"],
            "tools": ["pytest", "ruff", "mypy"],
        },
        "directory_structure": [
            "app/",
            "app/api/",
            "app/api/routes/",
            "app/models/",
            "app/schemas/",
            "app/core/",
            "app/db/",
            "tests/",
            "tests/api/",
            "alembic/",
            "docs/",
            "plan/",
        ],
    },
}


class TemplateSelector:
    """Selects the best template based on user requirements."""

    def select(
        self, platforms: list[str], tech_stack: dict[str, list[str]]
    ) -> dict[str, Any]:
        """Select the best matching template."""
        # Normalize inputs
        platforms_lower = [p.lower() for p in platforms]
        frontend_tech = [t.lower() for t in tech_stack.get("frontend", [])]
        backend_tech = [t.lower() for t in tech_stack.get("backend", [])]

        # Score each template
        best_template = None
        best_score = -1

        for template_id, template in TEMPLATES.items():
            score = self._score_template(
                template, platforms_lower, frontend_tech, backend_tech
            )
            if score > best_score:
                best_score = score
                best_template = template

        # Default to react-fastapi if no good match
        if best_template is None:
            best_template = TEMPLATES["react-fastapi"]

        return best_template

    def _score_template(
        self,
        template: dict[str, Any],
        platforms: list[str],
        frontend_tech: list[str],
        backend_tech: list[str],
    ) -> int:
        """Score a template based on how well it matches requirements."""
        score = 0

        # Platform matching
        template_platforms = [p.lower() for p in template["platforms"]]
        for platform in platforms:
            if platform in template_platforms:
                score += 10

        # Frontend tech matching
        template_frontend = [t.lower() for t in template["tech_stack"].get("frontend", [])]
        for tech in frontend_tech:
            if tech in template_frontend:
                score += 5

        # Backend tech matching
        template_backend = [t.lower() for t in template["tech_stack"].get("backend", [])]
        for tech in backend_tech:
            if tech in template_backend:
                score += 5

        return score

    def get_all_templates(self) -> dict[str, dict[str, Any]]:
        """Get all available templates."""
        return TEMPLATES.copy()

    def get_template(self, template_id: str) -> dict[str, Any] | None:
        """Get a specific template by ID."""
        return TEMPLATES.get(template_id)
