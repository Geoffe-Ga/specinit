"""Generation orchestrator for the 8-step process."""

import asyncio
import logging
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
from specinit.github.service import GitHubService
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
        additional_context: str | None = None,
        github_config: dict[str, Any] | None = None,
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
            "additional_context": additional_context,
            "template": template,
            "github_config": github_config,
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

            # GitHub integration (if configured)
            if github_config and github_config.get("enabled"):
                await self._github_integration(context, progress_callback)

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
        logger = logging.getLogger(__name__)

        def create_message() -> Any:
            logger.info(f"Creating message for step '{step_id}' with model '{self.model}'...")
            result = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            logger.info(f"Message created successfully for step '{step_id}'")
            return result

        # Add timeout to prevent hanging indefinitely (5 minutes should be enough for any API call)
        logger.info(f"Starting API call for step '{step_id}'...")
        try:
            response = await asyncio.wait_for(asyncio.to_thread(create_message), timeout=300.0)
            logger.info(f"API call completed for step '{step_id}'")
        except TimeoutError as e:
            logger.error(f"API call timed out for step '{step_id}'")
            raise RuntimeError(
                f"Claude API call timed out after 5 minutes for step '{step_id}'. "
                "This may indicate a network issue or API slowness."
            ) from e
        except Exception as e:
            logger.error(f"API call failed for step '{step_id}': {e}")
            raise

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
        logger = logging.getLogger(__name__)
        logger.info("Building product spec prompt...")
        prompt = self.prompt_builder.build_product_spec_prompt(context)
        logger.info(f"Prompt built, length: {len(prompt)} chars. Calling Claude API...")
        spec_content = await self._call_claude(prompt, "product_spec")
        logger.info(f"Received response from Claude API, length: {len(spec_content)} chars")

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
        """Step 7: Initialize Git repository.

        Issue #13 Fix: Properly check subprocess return codes and raise errors.
        """
        # Initialize git
        result = subprocess.run(
            ["git", "init"], cwd=self.project_path, capture_output=True, check=False
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Git init failed: {stderr}")

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
        # Stage all files
        result = subprocess.run(
            ["git", "add", "."], cwd=self.project_path, capture_output=True, check=False
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Git add failed: {stderr}")

        # Create commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.project_path,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            # Allow "nothing to commit" as a non-error
            if "nothing to commit" not in stderr.lower():
                raise RuntimeError(f"Git commit failed: {stderr}")

        self.file_writer.append(
            "plan/progress-notes.md",
            "\n## Step 7: Git Initialization\n- Repository initialized\n- Initial commit created\n",
        )

    async def _generate_demo_code(self, context: dict[str, Any]) -> None:
        """Step 8: Generate demo implementation code and README."""
        # Read the product spec for context
        spec_path = self.project_path / "plan" / "product-spec.md"
        spec_content = spec_path.read_text() if spec_path.exists() else ""

        prompt = self.prompt_builder.build_demo_code_prompt(context, spec_content)
        demo_code = await self._call_claude(prompt, "demo_code")

        # Parse and write demo code files
        self.file_writer.write_demo_code(demo_code)

        # Now generate README based on actual implementation
        await self._generate_readme(context, spec_content)

        self.file_writer.append(
            "plan/progress-notes.md",
            "\n## Step 8: Demo Code\n- Demo implementation generated\n- Tests included\n- README.md generated based on actual implementation\n",
        )

    async def _generate_readme(self, context: dict[str, Any], spec_content: str) -> None:
        """Generate README.md based on actual project implementation.

        This is called AFTER demo code is generated so the README can
        accurately reflect what was actually built.
        """
        # Collect list of generated files for context
        project_files: list[str] = []
        for path in self.project_path.rglob("*"):
            if path.is_file():
                try:
                    rel_path = path.relative_to(self.project_path)
                    # Skip common build/cache directories
                    if not any(
                        part.startswith(".")
                        or part in {"__pycache__", "node_modules", "dist", "build"}
                        for part in rel_path.parts
                    ):
                        project_files.append(str(rel_path))
                except ValueError:
                    continue

        # Sort for consistent ordering
        project_files.sort()

        # Build and call the README generation prompt
        prompt = self.prompt_builder.build_readme_prompt(context, spec_content, project_files)
        readme_content = await self._call_claude(prompt, "readme")

        # Write README to docs/ directory
        self.file_writer.write("docs/README.md", readme_content)

    async def _github_integration(
        self, context: dict[str, Any], progress_callback: ProgressCallback | None
    ) -> None:
        """Set up GitHub repository and create initial issues.

        This runs even in non-YOLO mode to provide basic GitHub integration:
        - Create repository (if needed)
        - Push initial commit
        - Create issues from product spec

        YOLO mode would additionally run the full automated workflow,
        but that's not part of this fix.
        """
        github_config = context.get("github_config")
        if not github_config:
            return

        if progress_callback:
            await progress_callback(
                "github_setup", "in_progress", {"name": "Setting up GitHub repository"}
            )

        try:
            # Get GitHub token from keyring
            token = GitHubService.get_token()
            if not token:
                # Token was supposed to be validated earlier, but handle gracefully
                if progress_callback:
                    await progress_callback(
                        "github_setup",
                        "skipped",
                        {"name": "GitHub token not found - please run: specinit config"},
                    )
                return

            # Parse and validate repo URL first (before creating service)
            repo_url = github_config.get("repo_url", "")
            if not repo_url:
                if progress_callback:
                    await progress_callback(
                        "github_setup",
                        "skipped",
                        {"name": "No repository URL provided"},
                    )
                return

            # Security validation - prevent command injection
            if repo_url.startswith("-"):
                if progress_callback:
                    await progress_callback(
                        "github_setup",
                        "failed",
                        {"name": "Invalid repository URL: cannot start with dash"},
                    )
                return

            # Use context manager to ensure session cleanup
            with GitHubService(token=token) as github:
                # Validate URL format and extract owner/repo
                try:
                    owner, repo_name = github.parse_repo_url(repo_url)
                except ValueError as e:
                    if progress_callback:
                        await progress_callback(
                            "github_setup",
                            "failed",
                            {"name": f"Invalid repository URL: {e}"},
                        )
                    return

                # Create repository if requested and doesn't exist
                if github_config.get("create_repo", False):
                    try:
                        if not github.repo_exists(owner, repo_name):
                            github.create_repo(
                                name=repo_name,
                                description=f"{context['project_name']} - "
                                f"As {context['user_story']['role']}, "
                                f"I want to {context['user_story']['action']}",
                                private=False,
                            )
                    except Exception as e:
                        if progress_callback:
                            await progress_callback(
                                "github_setup",
                                "failed",
                                {"name": f"Failed to create repository: {e}"},
                            )
                        return

                # Set up git remote and push initial commit
                try:
                    await asyncio.to_thread(self._setup_github_remote_and_push, repo_url)
                except subprocess.CalledProcessError as e:
                    if progress_callback:
                        await progress_callback(
                            "github_setup",
                            "failed",
                            {"name": f"Failed to push to GitHub: {e}"},
                        )
                    return

                # Create issues from product spec (unless YOLO mode which handles this differently)
                if not github_config.get("yolo_mode", False):
                    await self._create_github_issues(github, owner, repo_name, context)

                if progress_callback:
                    await progress_callback(
                        "github_setup",
                        "completed",
                        {"name": "GitHub repository configured and issues created"},
                    )

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"GitHub integration failed: {e}")
            if progress_callback:
                await progress_callback(
                    "github_setup",
                    "failed",
                    {"name": "GitHub integration failed: check your network connection"},
                )
            # Don't fail the whole generation if GitHub integration fails
            return

    def _setup_github_remote_and_push(self, repo_url: str) -> None:
        """Set up git remote and push initial commit."""
        # Add or update remote
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=self.project_path,
            capture_output=True,
            check=False,
        )

        if result.returncode == 0:
            # Update existing remote
            subprocess.run(
                ["git", "remote", "set-url", "origin", repo_url],
                cwd=self.project_path,
                check=True,
            )
        else:
            # Add new remote
            subprocess.run(
                ["git", "remote", "add", "origin", repo_url],
                cwd=self.project_path,
                check=True,
            )

        # Push to GitHub
        subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            cwd=self.project_path,
            check=True,
        )

    async def _create_github_issues(
        self, github: GitHubService, owner: str, repo_name: str, context: dict[str, Any]
    ) -> None:
        """Create GitHub issues from the product specification."""
        # Read product spec
        spec_path = self.project_path / "plan" / "product-spec.md"
        if not spec_path.exists():
            return

        # Create an issue for each feature
        for feature in context["features"]:
            issue_title = f"Implement: {feature[:80]}"  # Truncate to reasonable length
            issue_body = f"""## Feature Description
{feature}

## Context
This feature is part of the project requirements:

**User Story:**
As {context["user_story"]["role"]}, I want to {context["user_story"]["action"]},
so that {context["user_story"]["outcome"]}

## Reference
See the full product specification in `plan/product-spec.md` for architectural details.

## Acceptance Criteria
- [ ] Feature implementation matches the specification
- [ ] Tests are written and passing
- [ ] Documentation is updated
"""

            await asyncio.to_thread(
                github.create_issue,
                owner=owner,
                repo=repo_name,
                title=issue_title,
                body=issue_body,
                labels=["feature", "from-spec"],
            )
