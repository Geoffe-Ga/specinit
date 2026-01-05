"""Tests for AI suggestion prompt builders."""

import pytest

from specinit.generator.suggestion_prompts import (
    PROMPT_BUILDERS,
    build_aesthetics_prompt,
    build_feature_prompt,
    build_prompt,
    build_tech_stack_prompt,
    build_user_story_prompt,
)


class TestUserStoryPrompt:
    """Tests for user story prompt building."""

    def test_builds_basic_prompt(self):
        """Should build user story prompt with project description and platforms."""
        context = {
            "projectDescription": "A research note-taking app",
            "platforms": ["web", "ios"],
        }

        result = build_user_story_prompt(context, count=3)

        assert "A research note-taking app" in result
        assert "web, ios" in result
        assert "Generate 3 user stories" in result
        assert "As a [role], I want to [action], so that [outcome]" in result

    def test_handles_missing_description(self):
        """Should handle missing project description."""
        context = {"platforms": ["web"]}

        result = build_user_story_prompt(context, count=5)

        assert "Platforms: web" in result
        assert "Generate 5 user stories" in result

    def test_includes_current_value(self):
        """Should include current value when provided."""
        context = {"projectDescription": "A todo app"}
        current_value = "As a student, I want to"

        result = build_user_story_prompt(context, current_value=current_value)

        assert 'User has started with: "As a student, I want to"' in result

    def test_handles_empty_platforms(self):
        """Should use fallback when no platforms provided."""
        context = {"projectDescription": "An app"}

        result = build_user_story_prompt(context)

        assert "any platform" in result

    def test_handles_snake_case_keys(self):
        """Should handle snake_case context keys."""
        context = {
            "project_description": "A CLI tool",
            "platforms": ["cli"],
        }

        result = build_user_story_prompt(context)

        assert "A CLI tool" in result
        assert "cli" in result


class TestFeaturePrompt:
    """Tests for feature prompt building."""

    def test_builds_basic_prompt(self):
        """Should build feature prompt with user story."""
        context = {
            "userStory": {
                "role": "researcher",
                "action": "create daily notes",
                "outcome": "track my progress",
            },
            "platforms": ["web"],
        }

        result = build_feature_prompt(context, count=5)

        assert "As a researcher" in result
        assert "create daily notes" in result
        assert "track my progress" in result
        assert "Generate 5 specific features" in result
        assert "Platforms: web" in result

    def test_includes_current_value(self):
        """Should include current value when provided."""
        context = {"userStory": {"role": "user", "action": "login", "outcome": "access app"}}
        current_value = "Authentication with OAuth"

        result = build_feature_prompt(context, current_value=current_value)

        assert 'User has started with: "Authentication with OAuth"' in result

    def test_handles_empty_user_story(self):
        """Should handle missing user story fields."""
        context = {"platforms": ["ios"]}

        result = build_feature_prompt(context)

        assert "Platforms: ios" in result
        assert "As a , I want to , so that" in result

    def test_handles_snake_case_keys(self):
        """Should handle snake_case context keys."""
        context = {
            "user_story": {"role": "developer", "action": "test", "outcome": "verify"},
            "platforms": ["api"],
        }

        result = build_feature_prompt(context)

        assert "As a developer" in result


class TestTechStackPrompt:
    """Tests for tech stack prompt building."""

    def test_builds_basic_prompt(self):
        """Should build tech stack prompt with platforms and features."""
        context = {
            "platforms": ["web", "mobile"],
            "features": ["User authentication", "Real-time sync"],
        }

        result = build_tech_stack_prompt(context, count=3)

        assert "Platforms: web, mobile" in result
        assert "- User authentication" in result
        assert "- Real-time sync" in result
        assert "Suggest 3 technologies" in result

    def test_handles_empty_features(self):
        """Should use fallback when no features provided."""
        context = {"platforms": ["web"]}

        result = build_tech_stack_prompt(context)

        assert "- General application" in result

    def test_includes_current_value(self):
        """Should include current value when provided."""
        context = {"platforms": ["web"]}
        current_value = "React"

        result = build_tech_stack_prompt(context, current_value=current_value)

        assert 'User has started with: "React"' in result

    def test_handles_empty_platforms(self):
        """Should use fallback when no platforms provided."""
        context = {"features": ["Authentication"]}

        result = build_tech_stack_prompt(context)

        assert "any platform" in result


class TestAestheticsPrompt:
    """Tests for aesthetics prompt building."""

    def test_builds_basic_prompt(self):
        """Should build aesthetics prompt with platforms and features."""
        context = {
            "platforms": ["ios", "android"],
            "features": ["Photo sharing", "Social feed"],
        }

        result = build_aesthetics_prompt(context, count=3)

        assert "Platforms: ios, android" in result
        assert "- Photo sharing" in result
        assert "- Social feed" in result
        assert "Suggest 3 visual design styles" in result

    def test_handles_empty_features(self):
        """Should use fallback when no features provided."""
        context = {"platforms": ["web"]}

        result = build_aesthetics_prompt(context)

        assert "- General application" in result

    def test_includes_current_value(self):
        """Should include current value when provided."""
        context = {"platforms": ["web"]}
        current_value = "minimalist"

        result = build_aesthetics_prompt(context, current_value=current_value)

        assert 'User has started with: "minimalist"' in result

    def test_handles_empty_platforms(self):
        """Should use fallback when no platforms provided."""
        context = {"features": ["Dashboard"]}

        result = build_aesthetics_prompt(context)

        assert "any platform" in result


class TestBuildPrompt:
    """Tests for build_prompt dispatcher function."""

    def test_dispatches_to_user_stories(self):
        """Should dispatch to user story builder."""
        context = {"projectDescription": "An app"}

        result = build_prompt("user_stories", context)

        assert "An app" in result
        assert "user stories" in result

    def test_dispatches_to_features(self):
        """Should dispatch to features builder."""
        context = {"userStory": {"role": "user", "action": "do", "outcome": "win"}}

        result = build_prompt("features", context)

        assert "As a user" in result
        assert "features" in result

    def test_dispatches_to_tech_stack(self):
        """Should dispatch to tech stack builder."""
        context = {"platforms": ["web"]}

        result = build_prompt("tech_stack", context)

        assert "technologies" in result

    def test_dispatches_to_aesthetics(self):
        """Should dispatch to aesthetics builder."""
        context = {"platforms": ["mobile"]}

        result = build_prompt("aesthetics", context)

        assert "design styles" in result

    def test_raises_on_invalid_field(self):
        """Should raise ValueError for unsupported field types."""
        with pytest.raises(ValueError) as excinfo:
            build_prompt("invalid_field", {})

        assert "invalid_field" in str(excinfo.value)
        assert "not supported" in str(excinfo.value)

    def test_passes_count_parameter(self):
        """Should pass count parameter to builder."""
        result = build_prompt("user_stories", {}, count=10)

        assert "Generate 10 user stories" in result

    def test_passes_current_value(self):
        """Should pass current_value parameter to builder."""
        result = build_prompt("user_stories", {}, current_value="As a user")

        assert "As a user" in result


class TestPromptBuilders:
    """Tests for PROMPT_BUILDERS registry."""

    def test_contains_all_field_types(self):
        """Should contain all expected field type builders."""
        expected_fields = {"user_stories", "features", "tech_stack", "aesthetics"}

        assert set(PROMPT_BUILDERS.keys()) == expected_fields

    def test_all_builders_are_callable(self):
        """Should have callable builder functions for all fields."""
        for field, builder in PROMPT_BUILDERS.items():
            assert callable(builder), f"Builder for {field} is not callable"
