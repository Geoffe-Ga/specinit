"""Generation orchestrator for the 8-step process."""

import asyncio
import logging
import subprocess
import time
from collections.abc import Callable, Coroutine
from pathlib import Path, PurePath
from typing import Any, ClassVar, cast
from urllib.parse import urlparse

import requests
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

    def _read_previous_step_outputs(self) -> dict[str, str]:
        """Read all generated files from previous steps.

        Returns:
            Dictionary mapping relative file paths to their content.
        """
        outputs: dict[str, str] = {}
        max_file_size = 50_000  # 50KB limit per file

        # Directories and cache folders to skip
        skip_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            ".venv",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".tox",
            ".nox",
        }

        for path in self.project_path.rglob("*"):
            if not path.is_file():
                continue

            # Skip if any part of the path is in skip_dirs
            if any(part in skip_dirs for part in path.parts):
                continue

            try:
                rel_path = path.relative_to(self.project_path)
                content = path.read_text(encoding="utf-8")

                # Truncate large files
                if len(content) > max_file_size:
                    content = content[:max_file_size] + "\n\n[Truncated - file too large]"

                outputs[str(rel_path)] = content
            except (UnicodeDecodeError, OSError) as e:
                # Skip binary files and files that can't be read
                logger = logging.getLogger(__name__)
                logger.debug(f"Skipping file {path}: {e}")
                continue

        # Log context size metrics for debugging
        total_size = sum(len(content) for content in outputs.values())
        logger = logging.getLogger(__name__)
        logger.debug(
            f"Read {len(outputs)} files from previous steps (total size: {total_size:,} bytes)"
        )

        return outputs

    def _build_step_context(self, step_id: str, base_context: dict[str, Any]) -> dict[str, Any]:
        """Build context for a step, including outputs from previous steps.

        Implements step-specific context filtering to prevent context explosion.
        Each step only receives outputs from relevant previous steps.

        Args:
            step_id: The current step identifier
            base_context: The base context from generate()

        Returns:
            Context dictionary with previous_outputs added (if not first step)
        """
        # Copy base context
        step_context = base_context.copy()

        # Define which file patterns each step needs from previous steps
        # This prevents context explosion by limiting what gets passed to Claude API
        #
        # Steps with empty patterns ([]) either:
        # - Are first in the sequence (product_spec)
        # - Are local-only operations that don't call Claude API (validation, git_init)
        #
        # Note: dependencies step was changed to local-only in latest refactor,
        # but kept file patterns in case it needs Claude API calls in future.
        step_file_patterns: dict[str, list[str]] = {
            "product_spec": [],  # First step, no previous outputs needed
            "structure": ["plan/*.md"],  # Needs product spec to create directory structure
            "documentation": [
                "plan/*.md",  # Product spec for context
                "src/**/*",  # Generated structure to document
                "**/package.json",  # Project config
                "**/pyproject.toml",  # Project config
                "**/Cargo.toml",  # Project config
            ],
            "tooling": [
                "plan/*.md",  # Product spec for tech stack requirements
                "src/**/*",  # Structure to configure tools for
                "**/package.json",  # Dependencies for tool config
                "**/pyproject.toml",  # Dependencies for tool config
            ],
            "validation": [],  # Local-only: validates structure without API calls
            "dependencies": [
                "plan/*.md",  # Product spec for tech stack
                "src/**/*",  # Structure to understand dependencies
            ],
            "git_init": [],  # Local-only: initializes git repository without API calls
            "demo_code": [
                "plan/*.md",  # Product spec for feature requirements
                "src/**/*",  # All structure files
                "*.md",  # Documentation (README, CONTRIBUTING, CLAUDE.md)
                ".*rc*",  # Tool configs (.eslintrc, .prettierrc, etc.)
                "**/.*.json",  # Config files (.eslintrc.json, etc.)
                "**/package.json",  # Dependencies to use in demo code
                "**/pyproject.toml",  # Dependencies to use in demo code
                "**/Cargo.toml",  # Dependencies to use in demo code
            ],
        }

        # Get patterns for this step
        patterns = step_file_patterns.get(step_id, [])

        # If no patterns (first step or local-only steps), no previous outputs
        if not patterns:
            return step_context

        # Read all previous outputs
        all_outputs = self._read_previous_step_outputs()

        # Filter to only matching patterns
        # Use PurePath.match() instead of fnmatch for correct ** globstar handling
        filtered_outputs = {}
        for file_path, content in all_outputs.items():
            for pattern in patterns:
                if PurePath(file_path).match(pattern):
                    filtered_outputs[file_path] = content
                    break

        step_context["previous_outputs"] = filtered_outputs

        return step_context

    async def _execute_step(self, step_id: str, context: dict[str, Any]) -> None:
        """Execute a single generation step with accumulated context."""
        # Build step-specific context with previous outputs
        step_context = self._build_step_context(step_id, context)

        if step_id == "product_spec":
            await self._generate_product_spec(step_context)
        elif step_id == "structure":
            await self._create_structure(step_context)
        elif step_id == "documentation":
            await self._generate_documentation(step_context)
        elif step_id == "tooling":
            await self._configure_tooling(step_context)
        elif step_id == "validation":
            await self._validate_project(step_context)
        elif step_id == "dependencies":
            await self._setup_dependencies(step_context)
        elif step_id == "git_init":
            await self._init_git(step_context)
        elif step_id == "demo_code":
            await self._generate_demo_code(step_context)

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

        # Copy agent profile templates (Issue #101)
        self.file_writer.write_agent_profiles()

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

    def _validate_repo_url(self, repo_url: str) -> None:
        """Validate repository URL for security.

        Args:
            repo_url: The repository URL to validate

        Raises:
            ValueError: If the URL is invalid or potentially dangerous
        """
        parsed = urlparse(repo_url)

        # Validate URL structure
        if not parsed.netloc and "/" not in repo_url:
            # Might be short form "owner/repo", which is handled by parse_repo_url
            pass
        elif parsed.scheme and parsed.scheme not in ("https", "http", "ssh", "git"):
            # Reject dangerous schemes like file://, javascript:, data:, etc.
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

        # Check for dangerous characters that could be interpreted as flags
        if repo_url.startswith("-"):
            raise ValueError("URL cannot start with dash")

        # Check for shell metacharacters
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\r"]
        if any(char in repo_url for char in dangerous_chars):
            raise ValueError("URL contains unsafe shell characters")

    async def _report_github_status(
        self,
        progress_callback: ProgressCallback | None,
        status: str,
        message: str,
    ) -> None:
        """Report GitHub setup progress status.

        Args:
            progress_callback: Optional callback for progress updates
            status: Status type (in_progress, completed, failed, skipped)
            message: Status message to display
        """
        if progress_callback:
            await progress_callback("github_setup", status, {"name": message})

    async def _get_validated_github_token(
        self, progress_callback: ProgressCallback | None
    ) -> str | None:
        """Get and validate GitHub token from keyring.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            GitHub token if found and valid, None otherwise
        """
        token = GitHubService.get_token()
        if not token and progress_callback:
            await self._report_github_status(
                progress_callback,
                "skipped",
                "GitHub token not found - please run: specinit config",
            )
        return token

    async def _get_validated_repo_url(
        self,
        github_config: dict[str, Any],
        progress_callback: ProgressCallback | None,
    ) -> str | None:
        """Get and validate repository URL from config.

        Args:
            github_config: GitHub configuration dictionary
            progress_callback: Optional callback for progress updates

        Returns:
            Validated repository URL, or None if invalid/missing
        """
        repo_url: str = github_config.get("repo_url", "")
        if not repo_url:
            await self._report_github_status(
                progress_callback, "skipped", "No repository URL provided"
            )
            return None

        # Security validation - prevent command injection and malicious URLs
        try:
            self._validate_repo_url(repo_url)
        except ValueError as e:
            await self._report_github_status(
                progress_callback, "failed", f"Invalid repository URL: {e}"
            )
            return None

        return repo_url

    async def _create_repo_if_needed(
        self,
        github: GitHubService,
        owner: str,
        repo_name: str,
        context: dict[str, Any],
        github_config: dict[str, Any],
        progress_callback: ProgressCallback | None,
    ) -> bool:
        """Create GitHub repository if requested and it doesn't exist.

        Args:
            github: GitHub service instance
            owner: Repository owner
            repo_name: Repository name
            context: Project context dictionary
            github_config: GitHub configuration dictionary
            progress_callback: Optional callback for progress updates

        Returns:
            True if successful or not needed, False if creation failed
        """
        if not github_config.get("create_repo", False):
            return True

        try:
            if not github.repo_exists(owner, repo_name):
                github.create_repo(
                    name=repo_name,
                    description=f"{context['project_name']} - "
                    f"As {context['user_story']['role']}, "
                    f"I want to {context['user_story']['action']}",
                    private=github_config.get("private", False),
                )
        except Exception as e:
            await self._report_github_status(
                progress_callback, "failed", f"Failed to create repository: {e}"
            )
            return False

        return True

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

        await self._report_github_status(
            progress_callback, "in_progress", "Setting up GitHub repository"
        )

        try:
            # Get and validate GitHub token
            token = await self._get_validated_github_token(progress_callback)
            if not token:
                return

            # Get and validate repository URL
            repo_url = await self._get_validated_repo_url(github_config, progress_callback)
            if not repo_url:
                return

            # Use context manager to ensure session cleanup
            with GitHubService(token=token) as github:
                # Validate URL format and extract owner/repo
                try:
                    owner, repo_name = github.parse_repo_url(repo_url)
                except ValueError as e:
                    await self._report_github_status(
                        progress_callback, "failed", f"Invalid repository URL: {e}"
                    )
                    return

                # Create repository if requested and doesn't exist
                if not await self._create_repo_if_needed(
                    github, owner, repo_name, context, github_config, progress_callback
                ):
                    return

                # Set up git remote and push initial commit
                try:
                    await asyncio.to_thread(self._setup_github_remote_and_push, repo_url, token)
                except (subprocess.CalledProcessError, RuntimeError) as e:
                    await self._report_github_status(
                        progress_callback, "failed", f"Failed to push to GitHub: {e}"
                    )
                    return

                # Create issues from product spec (unless YOLO mode)
                if not github_config.get("yolo_mode", False):
                    await self._create_github_issues(github, owner, repo_name, context)

                await self._report_github_status(
                    progress_callback,
                    "completed",
                    "GitHub repository configured and issues created",
                )

        except (
            requests.exceptions.RequestException,
            subprocess.CalledProcessError,
            ValueError,
        ) as e:
            logger = logging.getLogger(__name__)
            logger.error("GitHub integration failed: %s", e, exc_info=True)
            await self._report_github_status(
                progress_callback,
                "failed",
                "GitHub integration failed: check your network connection",
            )
            # Don't fail the whole generation if GitHub integration fails
            return

    def _setup_github_remote_and_push(self, repo_url: str, token: str) -> None:
        """Set up git remote and push initial commit.

        Args:
            repo_url: The repository URL to push to
            token: GitHub personal access token for authentication
        """
        # Add or update remote
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=self.project_path,
            capture_output=True,
            check=False,
            timeout=10,  # Fast operation, 10s is generous
        )

        if result.returncode == 0:
            # Update existing remote
            subprocess.run(
                ["git", "remote", "set-url", "origin", repo_url],
                cwd=self.project_path,
                check=True,
                timeout=10,
            )
        else:
            # Add new remote
            subprocess.run(
                ["git", "remote", "add", "origin", repo_url],
                cwd=self.project_path,
                check=True,
                timeout=10,
            )

        # Ensure we're on main branch before pushing
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=self.project_path,
            check=True,
            timeout=10,
        )

        # Parse URL and inject credentials for HTTPS URLs
        parsed = urlparse(repo_url)

        # Only inject credentials for HTTPS (SSH doesn't need it)
        if parsed.scheme in ("https", "http"):
            # Build authenticated URL using standard git mechanism
            # Token is embedded in URL which is standard practice for CI/automation
            authenticated_url = (
                f"{parsed.scheme}://x-access-token:{token}@{parsed.netloc}{parsed.path}"
            )
        else:
            # SSH or other schemes - use as-is
            authenticated_url = repo_url

        try:
            # Push with credentials, capture output to prevent token leakage
            result = subprocess.run(
                ["git", "push", "-u", authenticated_url, "main"],
                cwd=self.project_path,
                capture_output=True,  # CRITICAL: prevent token in terminal
                check=True,
                timeout=300,  # 5 minutes for large repos with slow networks
            )
        except subprocess.CalledProcessError as e:
            # Redact token from error message before raising
            error_msg = e.stderr.decode() if e.stderr else str(e)
            if token in error_msg:
                error_msg = error_msg.replace(token, "***REDACTED***")
            raise RuntimeError(f"Git push failed: {error_msg}") from e
        finally:
            # Clean up: remove any cached credentials from git config
            subprocess.run(
                ["git", "config", "--unset", "credential.helper"],
                cwd=self.project_path,
                capture_output=True,
                check=False,  # OK if not set
            )

    async def _create_github_issues(
        self, github: GitHubService, owner: str, repo_name: str, context: dict[str, Any]
    ) -> None:
        """Create GitHub issues from the product specification."""
        # Create an issue for each feature
        for feature in context["features"]:
            # Truncate title to reasonable length with ellipsis if needed
            max_title_len = 80
            if len(feature) > max_title_len:
                issue_title = f"Implement: {feature[:max_title_len]}..."
            else:
                issue_title = f"Implement: {feature}"
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
