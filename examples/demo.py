#!/usr/bin/env python3
"""
Demo script showing SpecInit in action.

This demonstrates core functionality without making API calls:
- Template selection based on platforms and tech stack
- Cost estimation for project generation
- Prompt building for Claude API calls

Run from project root:
    python examples/demo.py
"""

from specinit.generator.cost import MODEL_PRICING, CostTracker
from specinit.generator.prompts import PromptBuilder
from specinit.generator.templates import TEMPLATES, TemplateSelector


def demo_template_selection() -> None:
    """Demonstrate template selection logic."""
    print("=" * 60)
    print("DEMO: Template Selection")
    print("=" * 60)

    selector = TemplateSelector()

    print("\nAvailable Templates:")
    print("-" * 40)
    for template_id, template in TEMPLATES.items():
        print(f"  {template_id}: {template['name']}")
        print(f"    Platforms: {', '.join(template['platforms'])}")
        print()

    # Demo scenarios - typed explicitly for mypy
    scenarios: list[dict[str, str | list[str] | dict[str, list[str]]]] = [
        {
            "name": "Web app with React + FastAPI",
            "platforms": ["web"],
            "tech_stack": {"frontend": ["react"], "backend": ["fastapi"]},
        },
        {
            "name": "Mobile app for iOS and Android",
            "platforms": ["ios", "android"],
            "tech_stack": {"frontend": ["react-native"], "backend": []},
        },
        {
            "name": "Command-line tool",
            "platforms": ["cli"],
            "tech_stack": {"frontend": [], "backend": ["python", "click"]},
        },
        {
            "name": "API backend service",
            "platforms": ["api"],
            "tech_stack": {"frontend": [], "backend": ["fastapi"]},
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['name']}")
        platforms = scenario["platforms"]
        tech_stack = scenario["tech_stack"]
        assert isinstance(platforms, list)
        assert isinstance(tech_stack, dict)
        template = selector.select(platforms, tech_stack)
        print(f"  Selected: {template['name']}")


def demo_cost_estimation() -> None:
    """Demonstrate cost tracking and estimation."""
    print("\n" + "=" * 60)
    print("DEMO: Cost Tracking")
    print("=" * 60)

    print("\nModel Pricing (per 1M tokens):")
    print("-" * 40)
    for model, pricing in MODEL_PRICING.items():
        if model != "default":
            print(f"  {model}:")
            print(f"    Input:  ${pricing['input']:.2f}")
            print(f"    Output: ${pricing['output']:.2f}")

    tracker = CostTracker()

    print("\nSimulated Generation (8 steps):")
    print("-" * 40)

    steps = [
        ("product_spec", 2500, 6000),
        ("structure", 3000, 1500),
        ("documentation", 4500, 9000),
        ("tooling", 3500, 2500),
        ("demo_code", 7000, 15000),
    ]

    for step_id, input_tokens, output_tokens in steps:
        cost = tracker.add_usage(step_id, input_tokens, output_tokens, "claude-sonnet-4-5-20250929")
        print(f"  {step_id:20s} {input_tokens:5d} in / {output_tokens:5d} out = ${cost:.4f}")

    print("-" * 40)
    print(f"  {'TOTAL':20s} ${tracker.get_total_cost():.4f}")

    input_total, output_total = tracker.get_total_tokens()
    print(f"\nToken Summary: {input_total:,} input + {output_total:,} output")

    # Estimate for a typical project
    min_cost, max_cost = tracker.estimate_cost(20000, 35000)
    print(f"Typical Project Estimate: ${min_cost:.2f} - ${max_cost:.2f}")


def demo_prompt_building() -> None:
    """Demonstrate prompt building for Claude API."""
    print("\n" + "=" * 60)
    print("DEMO: Prompt Building")
    print("=" * 60)

    builder = PromptBuilder()

    context = {
        "project_name": "time-tracker",
        "platforms": ["web"],
        "user_story": {
            "role": "freelance developer",
            "action": "track my time across projects",
            "outcome": "bill clients accurately",
        },
        "features": [
            "Time tracking with start/stop",
            "Project management",
            "Invoice generation",
            "Client portal",
        ],
        "tech_stack": {
            "frontend": ["React", "TypeScript", "Tailwind"],
            "backend": ["FastAPI", "Python"],
            "database": ["PostgreSQL"],
            "tools": ["pytest", "ESLint"],
        },
        "aesthetics": ["Professional", "Minimalist"],
        "template": {"name": "React + FastAPI Web App"},
    }

    print("\nSample Project Configuration:")
    print("-" * 40)
    print(f"  Name: {context['project_name']}")
    platforms = context["platforms"]
    assert isinstance(platforms, list)
    print(f"  Platforms: {', '.join(platforms)}")
    us = context["user_story"]
    assert isinstance(us, dict)
    print(f"  User Story: As {us['role']},")
    print(f"              I want to {us['action']},")
    print(f"              so that {us['outcome']}")
    features = context["features"]
    assert isinstance(features, list)
    print(f"  Features: {len(features)} features")
    tech = context["tech_stack"]
    assert isinstance(tech, dict)
    print(f"  Tech: {', '.join(tech['frontend'] + tech['backend'])}")

    prompt = builder.build_product_spec_prompt(context)
    print("\nGenerated Prompt Preview:")
    print("-" * 40)
    # Show first 600 chars
    preview = prompt[:600].rsplit(" ", 1)[0] + "..."
    print(preview)
    print(f"\n[Full prompt: {len(prompt):,} characters]")


def main() -> None:
    """Run all demos."""
    print("\n" + "*" * 60)
    print("*" + " " * 18 + "SPECINIT DEMO" + " " * 19 + "*")
    print("*" * 60)
    print("\nThis demo showcases SpecInit's core functionality.")
    print("No API calls are made - this demonstrates local logic.\n")

    demo_template_selection()
    demo_cost_estimation()
    demo_prompt_building()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nTo generate a real project:")
    print("  specinit init    # Set up your API key")
    print("  specinit new     # Start project generation")
    print()


if __name__ == "__main__":
    main()
