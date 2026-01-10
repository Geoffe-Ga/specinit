"""File writing utilities for generated content."""

import re
import shutil
from pathlib import Path
from typing import Any


class FileWriter:
    """Handles writing generated content to files."""

    def __init__(self, project_path: Path) -> None:
        """Initialize with the project root path."""
        self.project_path = project_path.resolve()

    def _validate_path(self, relative_path: str) -> Path:
        """Validate that a path stays within the project directory.

        Args:
            relative_path: The relative path to validate.

        Returns:
            The resolved absolute path.

        Raises:
            ValueError: If the path escapes the project directory (path traversal).
        """
        # Reject absolute paths immediately
        if relative_path.startswith("/") or (len(relative_path) > 1 and relative_path[1] == ":"):
            raise ValueError(
                f"Path traversal detected: absolute paths not allowed: {relative_path}"
            )

        # Resolve the full path
        full_path = (self.project_path / relative_path).resolve()

        # Verify it's within the project directory
        try:
            full_path.relative_to(self.project_path)
        except ValueError:
            raise ValueError(
                f"Path traversal detected: path escapes project directory: {relative_path}"
            ) from None

        return full_path

    def write(self, relative_path: str, content: str) -> Path:
        """Write content to a file, creating directories as needed."""
        file_path = self._validate_path(relative_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path

    def append(self, relative_path: str, content: str) -> Path:
        """Append content to an existing file."""
        file_path = self._validate_path(relative_path)
        if file_path.exists():
            existing = file_path.read_text()
            file_path.write_text(existing + content)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        return file_path

    def create_structure_from_script(self, script_content: str) -> None:
        """Parse a bash script and create the directory structure."""
        # Extract mkdir commands
        mkdir_pattern = r"mkdir\s+-p\s+([^\s]+)"
        for match in re.finditer(mkdir_pattern, script_content):
            dir_path = match.group(1).strip("'\"")
            full_path = self._validate_path(dir_path)
            full_path.mkdir(parents=True, exist_ok=True)

        # Extract touch commands
        touch_pattern = r"touch\s+([^\s]+)"
        for match in re.finditer(touch_pattern, script_content):
            file_path = match.group(1).strip("'\"")
            full_path = self._validate_path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()

    def write_documentation(self, content: str) -> None:
        """Parse documentation content and write to appropriate files."""
        self._parse_and_write_files(content)

    def write_tooling_configs(self, content: str) -> None:
        """Parse tooling config content and write to appropriate files."""
        self._parse_and_write_files(content)

    def write_demo_code(self, content: str) -> None:
        """Parse demo code content and write to appropriate files."""
        self._parse_and_write_files(content)

    def write_agent_profiles(self) -> None:
        """Copy agent profile templates to .claude/profiles/ directory."""
        # Get templates directory (project root is 4 parents up from this file)
        templates_dir = Path(__file__).parent.parent.parent.parent / "templates" / "agent-profiles"

        if not templates_dir.exists():
            return

        # Create .claude/profiles directory in generated project
        profiles_dir = self.project_path / ".claude" / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        # Copy all profile files
        for profile_file in templates_dir.glob("*.md"):
            dest = profiles_dir / profile_file.name
            shutil.copy2(profile_file, dest)

    def _parse_and_write_files(self, content: str) -> None:
        """Parse content in the --- FILE: path --- format and write files."""
        # Pattern to match file sections
        file_pattern = r"---\s*FILE:\s*([^\s-]+)\s*---\s*\n(.*?)(?=---\s*FILE:|$)"

        for match in re.finditer(file_pattern, content, re.DOTALL):
            file_path = match.group(1).strip()
            file_content = match.group(2).strip()

            # Clean up any markdown code block markers
            file_content = re.sub(r"^```\w*\n?", "", file_content)
            file_content = re.sub(r"\n?```$", "", file_content)

            self.write(file_path, file_content + "\n")

    def write_gitignore(self, _tech_stack: dict[str, list[str]]) -> None:
        """Generate and write a .gitignore file based on tech stack."""
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.py[cod]
*$py.class
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/
.nox/

# Build outputs
*.log
*.pot
*.pyc

# Local config
.env.local
.env.*.local
*.local

# Database
*.db
*.sqlite3

# Frontend builds
.next/
out/
.nuxt/
.output/
.cache/

# Misc
*.bak
*.tmp
"""
        self.write(".gitignore", gitignore_content)

    def validate_structure(self, template: dict[str, Any]) -> dict[str, Any]:
        """Validate that the project structure matches the template."""
        missing_dirs: list[str] = []
        missing_files: list[str] = []
        results: dict[str, Any] = {
            "valid": True,
            "missing_dirs": missing_dirs,
            "missing_files": missing_files,
        }

        # Check required directories from template
        for dir_path in template.get("directory_structure", []):
            full_path = self.project_path / dir_path
            if not full_path.exists():
                results["valid"] = False
                missing_dirs.append(dir_path)

        # Check for plan directory (always required)
        plan_path = self.project_path / "plan"
        if not plan_path.exists():
            results["valid"] = False
            missing_dirs.append("plan/")

        # Check for required plan files
        required_plan_files = [
            "plan/product-spec.md",
            "plan/progress-notes.md",
            "plan/audit-log.md",
        ]
        for file_path in required_plan_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                results["valid"] = False
                missing_files.append(file_path)

        return results
