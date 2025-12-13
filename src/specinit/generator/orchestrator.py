"""Generation orchestrator for the 8-step process."""

import asyncio
import subprocess
import time
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, ClassVar, cast

from anthropic import Anthropic

from specinit.generator.cost import CostTracker
from specinit.generator.file_writer import FileWriter
from specinit.generator.prompts import PromptBuilder
from specinit.generator.templates import TemplateSelector
from specinit.storage.config import ConfigManager
from specinit.storage.history import HistoryManager

ProgressCallback = Callable[[str, str, dict | None], Coroutine[Any, Any, None]]


class GenerationOrchestrator:
    """Orchestrates the 8-step project generation process."""

    STEPS: ClassVar[list[tuple[str, str]]] = [
        ("product_spec", "Generating product specification"),
        ("structure", "Creating project structure"),
        ("documentation", "Writing documentation"),
        ("tooling", "Configuring developer tooling"),
        ("validation", "Validating configuration"),
        ("dependencies", "Setting up dependencies"),
        ("git_init", "Initializing Git repository"),
        ("demo_code", "Generating demo code"),
    ]

    def __init__(self, output_dir: Path, project_name: str) -> None:
        """Initialize the orchestrator."""
        self.output_dir = output_dir
        self.project_name = project_name
        self.project_path = output_dir / project_name

        self.config = ConfigManager()
        self.history = HistoryManager()
        self.cost_tracker = CostTracker()
        self.file_writer = FileWriter(self.project_path)
        self.prompt_builder = PromptBuilder()
        self.template_selector = TemplateSelector()

        self.client = Anthropic(api_key=self.config.get_api_key())
        self.model = self.config.get("api.model", "claude-sonnet-4-5-20250929")

    async def generate(
        self,
        platforms: list[str],
        user_story: dict[str, str],
        features: list[str],
        tech_stack: dict[str, list[str]],
        aesthetics: list[str],
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """Run the full generation process."""
        start_time = time.time()

        # Create project directory
        self.project_path.mkdir(parents=True, exist_ok=True)

        # Select template based on platforms and tech stack
        template = self.template_selector.select(platforms, tech_stack)

        # Build context for prompts
        context = {
            "project_name": self.project_name,
            "platforms": platforms,
            "user_story": user_story,
            "features": features,
            "tech_stack": tech_stack,
            "aesthetics": aesthetics,
            "template": template,
        }

        # Track project in history
        project_id = self.history.add_project(
            name=self.project_name,
            path=str(self.project_path),
            template=template["name"],
            platforms=platforms,
            tech_stack=list(tech_stack.get("frontend", [])) + list(tech_stack.get("backend", [])),
            status="in_progress",
        )

        try:
            # Execute each step
            for step_id, step_name in self.STEPS:
                if progress_callback:
                    await progress_callback(step_id, "in_progress", {"name": step_name})

                await self._execute_step(step_id, context)

                if progress_callback:
                    await progress_callback(
                        step_id,
                        "completed",
                        {
                            "name": step_name,
                            "cost": self.cost_tracker.get_step_cost(step_id),
                        },
                    )

            # Calculate final stats
            generation_time = time.time() - start_time
            total_cost = self.cost_tracker.get_total_cost()

            # Update history
            self.history.update_project(
                project_id,
                cost=total_cost,
                generation_time_seconds=generation_time,
                status="completed",
            )

            # Update config usage stats
            self.config.update_usage(total_cost)

            return {
                "path": self.project_path,
                "total_cost": total_cost,
                "generation_time": generation_time,
            }

        except Exception:
            self.history.update_project(project_id, status="failed")
            raise

    async def _execute_step(self, step_id: str, context: dict[str, Any]) -> None:
        """Execute a single generation step."""
        if step_id == "product_spec":
            await self._generate_product_spec(context)
        elif step_id == "structure":
            await self._create_structure(context)
        elif step_id == "documentation":
            await self._generate_documentation(context)
        elif step_id == "tooling":
            await self._configure_tooling(context)
        elif step_id == "validation":
            await self._validate_project(context)
        elif step_id == "dependencies":
            await self._setup_dependencies(context)
        elif step_id == "git_init":
            await self._init_git(context)
        elif step_id == "demo_code":
            await self._generate_demo_code(context)

    async def _call_claude(self, prompt: str, step_id: str) -> str:
        """Make a Claude API call and track costs."""

        def create_message() -> Any:
            return self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )

        response = await asyncio.to_thread(create_message)

        # Track costs
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        self.cost_tracker.add_usage(step_id, input_tokens, output_tokens, self.model)

        # Extract text from the first content block
        content_block = response.content[0]
        if hasattr(content_block, "text"):
            return cast(str, content_block.text)
        raise ValueError(f"Unexpected content block type: {type(content_block)}")

    async def _generate_product_spec(self, context: dict[str, Any]) -> None:
        """Step 1: Generate product specification."""
        prompt = self.prompt_builder.build_product_spec_prompt(context)
        spec_content = await self._call_claude(prompt, "product_spec")

        # Write to plan directory
        self.file_writer.write("plan/product-spec.md", spec_content)
        self.file_writer.write(
            "plan/progress-notes.md",
            "# Progress Notes\n\n## Step 1: Product Specification\n- Completed\n- Generated comprehensive spec\n",
        )
        self.file_writer.write(
            "plan/audit-log.md", "# Audit Log\n\n## Step 1 Audit\n- Product spec generated\n"
        )

    async def _create_structure(self, context: dict[str, Any]) -> None:
        """Step 2: Create project structure."""
        prompt = self.prompt_builder.build_structure_prompt(context)
        structure_script = await self._call_claude(prompt, "structure")

        # Parse and execute the structure creation
        self.file_writer.create_structure_from_script(structure_script)

    async def _generate_documentation(self, context: dict[str, Any]) -> None:
        """Step 3: Generate documentation."""
        prompt = self.prompt_builder.build_documentation_prompt(context)
        docs_content = await self._call_claude(prompt, "documentation")

        # Parse and write documentation files
        self.file_writer.write_documentation(docs_content)

    async def _configure_tooling(self, context: dict[str, Any]) -> None:
        """Step 4: Configure developer tooling."""
        prompt = self.prompt_builder.build_tooling_prompt(context)
        tooling_content = await self._call_claude(prompt, "tooling")

        # Parse and write config files
        self.file_writer.write_tooling_configs(tooling_content)

    async def _validate_project(self, context: dict[str, Any]) -> None:
        """Step 5: Validate project structure and configs."""
        # This is a local validation step, no API calls
        validation_results = self.file_writer.validate_structure(context["template"])

        self.file_writer.append(
            "plan/progress-notes.md",
            f"\n## Step 5: Validation\n- Validated project structure\n- Results: {validation_results}\n",
        )

    async def _setup_dependencies(self, _context: dict[str, Any]) -> None:
        """Step 6: Set up project dependencies."""
        # This is a local step - just prepare dependency files
        # Actual installation happens when user runs npm install / pip install
        self.file_writer.append(
            "plan/progress-notes.md",
            "\n## Step 6: Dependencies\n- Dependency files created\n- Run 'npm install' or 'pip install -e .' to install\n",
        )

    async def _init_git(self, context: dict[str, Any]) -> None:
        """Step 7: Initialize Git repository."""
        # Initialize git
        subprocess.run(["git", "init"], cwd=self.project_path, capture_output=True, check=False)

        # Create .gitignore if not exists
        gitignore_path = self.project_path / ".gitignore"
        if not gitignore_path.exists():
            self.file_writer.write_gitignore(context["tech_stack"])

        # Initial commit
        user_story = context["user_story"]
        features = context["features"]

        commit_message = f"""Initial commit: {self.project_name}

User Story: As {user_story["role"]}, I want to {user_story["action"]}, so that {user_story["outcome"]}

Features:
{chr(10).join(f"- {f}" for f in features)}

Generated with SpecInit
"""
        subprocess.run(["git", "add", "."], cwd=self.project_path, capture_output=True, check=False)
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.project_path,
            capture_output=True,
            check=False,
        )

        self.file_writer.append(
            "plan/progress-notes.md",
            "\n## Step 7: Git Initialization\n- Repository initialized\n- Initial commit created\n",
        )

    async def _generate_demo_code(self, context: dict[str, Any]) -> None:
        """Step 8: Generate demo implementation code."""
        # Read the product spec for context
        spec_path = self.project_path / "plan" / "product-spec.md"
        spec_content = spec_path.read_text() if spec_path.exists() else ""

        prompt = self.prompt_builder.build_demo_code_prompt(context, spec_content)
        demo_code = await self._call_claude(prompt, "demo_code")

        # Parse and write demo code files
        self.file_writer.write_demo_code(demo_code)

        self.file_writer.append(
            "plan/progress-notes.md",
            "\n## Step 8: Demo Code\n- Demo implementation generated\n- Tests included\n",
        )
