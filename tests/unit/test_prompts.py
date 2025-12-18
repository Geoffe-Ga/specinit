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
