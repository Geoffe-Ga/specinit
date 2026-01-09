"""Vulture whitelist - Known false positives for dead code detection.

This file lists code patterns that vulture incorrectly reports as unused.
These are typically framework callbacks, CLI decorators, Pydantic fields,
and test fixtures.

Add items here if vulture reports them as unused but they are:
1. Called by a framework (Click, FastAPI, pytest)
2. Used for serialization (Pydantic models)
3. Part of a public API

Issue #81: World-class complexity standards
"""

# ==============================================================================
# Click CLI commands - decorated functions called by Click framework
# ==============================================================================
cli  # specinit.cli.main - main CLI group
init  # specinit.cli.main - init command
new  # specinit.cli.main - new command
list  # specinit.cli.main - list command (shadows builtin intentionally)
config  # specinit.cli.main - config group
config_show  # specinit.cli.main - config show command
config_set  # specinit.cli.main - config set command
config_reset  # specinit.cli.main - config reset command
validate_port  # specinit.cli.main - Click callback

# ==============================================================================
# FastAPI routes - called by framework, not directly
# ==============================================================================
health_check  # specinit.server.app
get_config  # specinit.server.app
validate_github_token  # specinit.server.app
github_status  # specinit.server.app
estimate_cost  # specinit.server.app
get_suggestions  # specinit.server.app
generate_project  # specinit.server.app
serve_frontend  # specinit.server.app

# ==============================================================================
# Pydantic model fields - used for validation/serialization
# ==============================================================================
# GitHubConfigModel
enabled
repo_url
create_repo
yolo_mode
token_configured

# ProjectConfig
project_description
platforms
user_story
features
tech_stack
aesthetics
github
additional_context

# CostEstimate
min_cost
max_cost
breakdown

# SuggestionRequest/Response
field
context
current_value
count
suggestions
cost
tokens_used

# ==============================================================================
# Pydantic validators
# ==============================================================================
validate_features  # ProjectConfig.validate_features

# ==============================================================================
# Dataclass fields - used by callers/framework
# ==============================================================================
# Issue, PullRequest
state
url
mergeable
ci_status

# WorkflowIssue
branch_name
pr
dependencies
fix_attempts
error_message

# CoverageThresholds (some documented as not yet enforced)
overall
logic
ui
tests

# GitHubConfig
owner
repo
base_branch
auto_merge
max_fix_attempts
parallel_branches
iterate_on_precommit
iterate_on_ci
iterate_on_coverage
claude_code_review
coverage_thresholds
ci_timeout_seconds
ci_poll_interval
review_poll_interval

# ==============================================================================
# Context managers and special methods
# ==============================================================================
__enter__  # GitHubService
__exit__  # GitHubService

# ==============================================================================
# Module exports
# ==============================================================================
__version__  # specinit.__init__

# ==============================================================================
# Public API methods - intentionally unused in codebase but part of public API
# ==============================================================================
# CostTracker API
get_breakdown  # specinit.generator.cost

# TemplateSelector API
get_all_templates  # specinit.generator.templates
get_template  # specinit.generator.templates

# GitHubService API
delete_token  # specinit.github.service
get_issues  # specinit.github.service
close_issue  # specinit.github.service
get_pull_request  # specinit.github.service
get_workflow_runs  # specinit.github.service
get_workflow_run_logs  # specinit.github.service
setup_git_remote  # specinit.github.service

# GitHubWorkflow API
setup_repository  # specinit.github.workflow
create_issues_from_spec  # specinit.github.workflow
run_parallel  # specinit.github.workflow
get_status_summary  # specinit.github.workflow

# HistoryManager API
get_by_name  # specinit.storage.history
get_project_count  # specinit.storage.history
row_factory  # specinit.storage.history - SQLite attribute

# Server API
get_shutdown_event  # specinit.server.app

# ==============================================================================
# Constants used in tests
# ==============================================================================
CHANGES_REQUESTED  # specinit.github.workflow - used in tests
BLOCKED  # specinit.github.workflow - used in tests

# ==============================================================================
# Test fixtures (defined in conftest.py, used by pytest)
# ==============================================================================
temp_dir
mock_home
_mock_home
