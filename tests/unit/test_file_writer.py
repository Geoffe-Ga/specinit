"""Tests for file writer utilities."""


from specinit.generator.file_writer import FileWriter


class TestFileWriter:
    """Tests for FileWriter."""

    def test_write_creates_file(self, temp_dir):
        """write should create file with content."""
        writer = FileWriter(temp_dir)

        writer.write("test.txt", "Hello, World!")

        file_path = temp_dir / "test.txt"
        assert file_path.exists()
        assert file_path.read_text() == "Hello, World!"

    def test_write_creates_parent_directories(self, temp_dir):
        """write should create parent directories if needed."""
        writer = FileWriter(temp_dir)

        writer.write("deep/nested/path/file.txt", "Content")

        file_path = temp_dir / "deep" / "nested" / "path" / "file.txt"
        assert file_path.exists()

    def test_append_to_existing_file(self, temp_dir):
        """append should add content to existing file."""
        writer = FileWriter(temp_dir)

        writer.write("test.txt", "Line 1\n")
        writer.append("test.txt", "Line 2\n")

        file_path = temp_dir / "test.txt"
        content = file_path.read_text()
        assert "Line 1" in content
        assert "Line 2" in content

    def test_append_creates_file_if_not_exists(self, temp_dir):
        """append should create file if it doesn't exist."""
        writer = FileWriter(temp_dir)

        writer.append("new.txt", "Content")

        file_path = temp_dir / "new.txt"
        assert file_path.exists()

    def test_create_structure_from_script_mkdir(self, temp_dir):
        """create_structure_from_script should parse mkdir commands."""
        writer = FileWriter(temp_dir)

        script = """#!/bin/bash
mkdir -p src/components
mkdir -p tests
mkdir -p docs
"""
        writer.create_structure_from_script(script)

        assert (temp_dir / "src" / "components").exists()
        assert (temp_dir / "tests").exists()
        assert (temp_dir / "docs").exists()

    def test_create_structure_from_script_touch(self, temp_dir):
        """create_structure_from_script should parse touch commands."""
        writer = FileWriter(temp_dir)

        script = """#!/bin/bash
mkdir -p src
touch src/__init__.py
touch README.md
"""
        writer.create_structure_from_script(script)

        assert (temp_dir / "src" / "__init__.py").exists()
        assert (temp_dir / "README.md").exists()

    def test_parse_and_write_files(self, temp_dir):
        """_parse_and_write_files should handle FILE format."""
        writer = FileWriter(temp_dir)

        content = """--- FILE: src/main.py ---
def main():
    print("Hello")

--- FILE: tests/test_main.py ---
def test_main():
    assert True
"""
        writer._parse_and_write_files(content)

        assert (temp_dir / "src" / "main.py").exists()
        assert (temp_dir / "tests" / "test_main.py").exists()
        assert "def main" in (temp_dir / "src" / "main.py").read_text()

    def test_write_gitignore(self, temp_dir):
        """write_gitignore should create comprehensive .gitignore."""
        writer = FileWriter(temp_dir)

        writer.write_gitignore({"frontend": ["react"], "backend": ["python"]})

        gitignore = temp_dir / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "node_modules" in content
        assert "__pycache__" in content
        assert ".env" in content

    def test_validate_structure_valid(self, temp_dir):
        """validate_structure should pass for valid structure."""
        writer = FileWriter(temp_dir)

        # Create required directories
        (temp_dir / "plan").mkdir()
        (temp_dir / "plan" / "product-spec.md").write_text("Spec")
        (temp_dir / "plan" / "progress-notes.md").write_text("Notes")
        (temp_dir / "plan" / "audit-log.md").write_text("Log")
        (temp_dir / "src").mkdir()

        template = {"directory_structure": ["src/"]}

        result = writer.validate_structure(template)

        assert result["valid"] is True
        assert len(result["missing_dirs"]) == 0
        assert len(result["missing_files"]) == 0

    def test_validate_structure_missing_plan(self, temp_dir):
        """validate_structure should fail if plan/ is missing."""
        writer = FileWriter(temp_dir)

        template = {"directory_structure": ["src/"]}

        result = writer.validate_structure(template)

        assert result["valid"] is False
        assert "plan/" in result["missing_dirs"]
