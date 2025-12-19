"""Tests for prompt generation."""

from specinit.generator.prompts import PromptBuilder


class TestPromptBuilder:
    """Tests for PromptBuilder class."""

    def test_product_spec_prompt_without_additional_context(self):
        """Product spec prompt should work without additional context."""
        builder = PromptBuilder()
        context = {
            "project_name": "test-project",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": ["minimalist"],
        }

        prompt = builder.build_product_spec_prompt(context)

        assert "test-project" in prompt
        assert "Feature 1" in prompt
        assert "## Additional Context" not in prompt

    def test_product_spec_prompt_includes_additional_context(self):
        """Product spec prompt should include additional context when provided."""
        builder = PromptBuilder()
        context = {
            "project_name": "test-project",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": ["minimalist"],
            "additional_context": "Must use Clean Architecture principles",
        }

        prompt = builder.build_product_spec_prompt(context)

        assert "## Additional Context" in prompt
        assert "Must use Clean Architecture principles" in prompt

    def test_demo_code_prompt_without_additional_context(self):
        """Demo code prompt should work without additional context."""
        builder = PromptBuilder()
        context = {
            "project_name": "test-project",
            "features": ["Feature 1"],
        }
        spec_content = "Sample specification content"

        prompt = builder.build_demo_code_prompt(context, spec_content)

        assert "test-project" in prompt
        assert "Sample specification content" in prompt
        assert "## Additional Context" not in prompt

    def test_demo_code_prompt_includes_additional_context(self):
        """Demo code prompt should include additional context when provided."""
        builder = PromptBuilder()
        context = {
            "project_name": "test-project",
            "features": ["Feature 1"],
            "additional_context": "All code must follow TDD practices",
        }
        spec_content = "Sample specification content"

        prompt = builder.build_demo_code_prompt(context, spec_content)

        assert "## Additional Context" in prompt
        assert "All code must follow TDD practices" in prompt

    def test_additional_context_with_special_characters(self):
        """Additional context should handle special characters properly."""
        builder = PromptBuilder()
        context = {
            "project_name": "test",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": ["minimalist"],
            "additional_context": "Use {braces}, [brackets], and <tags>",
        }

        prompt = builder.build_product_spec_prompt(context)

        assert "Use {braces}, [brackets], and <tags>" in prompt

    def test_additional_context_with_newlines(self):
        """Additional context should preserve newlines."""
        builder = PromptBuilder()
        context = {
            "project_name": "test",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": ["minimalist"],
            "additional_context": "Line 1\nLine 2\nLine 3",
        }

        prompt = builder.build_product_spec_prompt(context)

        assert "Line 1\nLine 2\nLine 3" in prompt

    def test_readme_prompt_basic_generation(self):
        """README prompt should include spec content and project files."""
        builder = PromptBuilder()
        context = {
            "project_name": "test-project",
            "platforms": ["web"],
            "user_story": {"role": "developer", "action": "build app", "outcome": "deploy it"},
            "features": ["User authentication", "Data visualization"],
            "tech_stack": {
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            "aesthetics": ["modern"],
        }
        spec_content = "# Product Spec\n\nThis is a test specification."
        project_files = ["src/main.py", "tests/test_main.py", "README.md"]

        prompt = builder.build_readme_prompt(context, spec_content, project_files)

        assert "test-project" in prompt
        assert "User authentication" in prompt
        assert "Data visualization" in prompt
        assert "src/main.py" in prompt
        assert "tests/test_main.py" in prompt

    def test_readme_prompt_includes_spec_content(self):
        """README prompt should include product specification."""
        builder = PromptBuilder()
        context = {
            "project_name": "test",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": [],
        }
        spec_content = "UNIQUE_SPEC_CONTENT_12345"
        project_files = ["main.py"]

        prompt = builder.build_readme_prompt(context, spec_content, project_files)

        assert "UNIQUE_SPEC_CONTENT_12345" in prompt

    def test_readme_prompt_handles_many_files(self):
        """README prompt should handle projects with many files."""
        builder = PromptBuilder()
        context = {
            "project_name": "large-project",
            "platforms": ["web", "mobile"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": [],
        }
        spec_content = "Spec"
        # Create a list of many files
        project_files = [f"src/module{i}.py" for i in range(50)]

        prompt = builder.build_readme_prompt(context, spec_content, project_files)

        # Should include project name and at least some files
        assert "large-project" in prompt
        assert "src/module0.py" in prompt

    def test_readme_prompt_includes_platform_info(self):
        """README prompt should include platform-specific information."""
        builder = PromptBuilder()
        context = {
            "project_name": "multi-platform",
            "platforms": ["web", "ios", "android"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": [],
        }
        spec_content = "Spec"
        project_files = ["app.py"]

        prompt = builder.build_readme_prompt(context, spec_content, project_files)

        # Should mention platforms
        assert "web" in prompt.lower() or "platforms" in prompt.lower()

    def test_readme_prompt_with_additional_context(self):
        """README prompt should include additional context when provided."""
        builder = PromptBuilder()
        context = {
            "project_name": "test",
            "platforms": ["web"],
            "user_story": {"role": "user", "action": "test", "outcome": "success"},
            "features": ["Feature 1"],
            "tech_stack": {"frontend": [], "backend": [], "database": [], "tools": []},
            "aesthetics": [],
            "additional_context": "This project uses Clean Architecture",
        }
        spec_content = "Spec"
        project_files = ["main.py"]

        prompt = builder.build_readme_prompt(context, spec_content, project_files)

        assert "This project uses Clean Architecture" in prompt
