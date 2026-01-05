"""Prompt templates for AI-powered suggestions."""

from typing import Any


def build_user_story_prompt(
    context: dict[str, Any], count: int = 3, current_value: str = ""
) -> str:
    """Build prompt for user story suggestions.

    Args:
        context: Project context including description, platforms
        count: Number of suggestions to generate
        current_value: Partial user input to refine suggestions

    Returns:
        Formatted prompt for Claude API
    """
    description = context.get("project_description", context.get("projectDescription", ""))
    platforms = context.get("platforms", [])
    platform_str = ", ".join(platforms) if platforms else "any platform"

    prompt = f"""Given this project description: "{description}"

Platforms: {platform_str}
"""

    if current_value:
        prompt += f'\nUser has started with: "{current_value}"\n'

    prompt += f"""
Generate {count} user stories in the format:
"As a [role], I want to [action], so that [outcome]"

Focus on core functionality that would be essential for this type of application.
Return ONLY the user stories, one per line, without numbering or additional commentary."""

    return prompt


def build_feature_prompt(context: dict[str, Any], count: int = 3, current_value: str = "") -> str:
    """Build prompt for feature suggestions.

    Args:
        context: Project context including user story
        count: Number of suggestions to generate
        current_value: Partial user input to refine suggestions

    Returns:
        Formatted prompt for Claude API
    """
    user_story = context.get("userStory", context.get("user_story", {}))
    role = user_story.get("role", "")
    action = user_story.get("action", "")
    outcome = user_story.get("outcome", "")

    platforms = context.get("platforms", [])
    platform_str = ", ".join(platforms) if platforms else "any platform"

    prompt = f"""Given this user story:
"As a {role}, I want to {action}, so that {outcome}"

Platforms: {platform_str}
"""

    if current_value:
        prompt += f'\nUser has started with: "{current_value}"\n'

    prompt += f"""
Generate {count} specific features needed to fulfill this user story.

Focus on:
- Core functionality
- User interface components
- Data management
- User experience enhancements

Return ONLY the feature names, one per line, without numbering or additional commentary."""

    return prompt


def build_tech_stack_prompt(
    context: dict[str, Any], count: int = 3, current_value: str = ""
) -> str:
    """Build prompt for tech stack suggestions.

    Args:
        context: Project context including features and platforms
        count: Number of suggestions to generate
        current_value: Partial user input to refine suggestions

    Returns:
        Formatted prompt for Claude API
    """
    platforms = context.get("platforms", [])
    features = context.get("features", [])

    platform_str = ", ".join(platforms) if platforms else "any platform"
    features_str = "\n".join(f"- {f}" for f in features) if features else "- General application"

    prompt = f"""Given these requirements:

Platforms: {platform_str}

Features:
{features_str}
"""

    if current_value:
        prompt += f'\nUser has started with: "{current_value}"\n'

    prompt += f"""
Suggest {count} technologies or frameworks that would be well-suited for this project.

Consider:
- Platform compatibility
- Feature requirements
- Development efficiency
- Community support
- Modern best practices

Return ONLY the technology names, one per line, without numbering or additional commentary."""

    return prompt


def build_aesthetics_prompt(
    context: dict[str, Any], count: int = 3, current_value: str = ""
) -> str:
    """Build prompt for aesthetic/visual style suggestions.

    Args:
        context: Project context including features and platforms
        count: Number of suggestions to generate
        current_value: Partial user input to refine suggestions

    Returns:
        Formatted prompt for Claude API
    """
    platforms = context.get("platforms", [])
    features = context.get("features", [])

    platform_str = ", ".join(platforms) if platforms else "any platform"
    features_str = "\n".join(f"- {f}" for f in features) if features else "- General application"

    prompt = f"""Given these requirements:

Platforms: {platform_str}

Features:
{features_str}
"""

    if current_value:
        prompt += f'\nUser has started with: "{current_value}"\n'

    prompt += f"""
Suggest {count} visual design styles or aesthetics that would be appropriate for this application.

Consider:
- Platform design guidelines (iOS, Android, web)
- User expectations for this type of app
- Modern design trends
- Accessibility

Return ONLY the aesthetic style names (e.g., "minimalist", "modern", "playful"), one per line, without numbering or additional commentary."""

    return prompt


PROMPT_BUILDERS = {
    "user_stories": build_user_story_prompt,
    "features": build_feature_prompt,
    "tech_stack": build_tech_stack_prompt,
    "aesthetics": build_aesthetics_prompt,
}


def build_prompt(
    field: str, context: dict[str, Any], count: int = 3, current_value: str = ""
) -> str:
    """Build a prompt for the specified field type.

    Args:
        field: Field type (user_stories, features, tech_stack, aesthetics)
        context: Project context
        count: Number of suggestions to generate
        current_value: Partial user input

    Returns:
        Formatted prompt for Claude API

    Raises:
        ValueError: If field type is not supported
    """
    if field not in PROMPT_BUILDERS:
        raise ValueError(
            f"Field '{field}' is not supported. Supported fields: {list(PROMPT_BUILDERS.keys())}"
        )

    builder = PROMPT_BUILDERS[field]
    return builder(context, count, current_value)
