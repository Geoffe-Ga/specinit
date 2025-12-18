"""FastAPI server for SpecInit web interface."""

import asyncio
import json
from contextvars import ContextVar
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError, field_validator

from specinit.generator.orchestrator import GenerationOrchestrator
from specinit.github.service import GitHubService
from specinit.storage.config import ConfigManager

app = FastAPI(title="SpecInit", description="AI-powered project initialization")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8765"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Issue #10 Fix: Use context variables for async context isolation
# This replaces global mutable state to prevent race conditions
# Note: We use None as default and initialize lazily to avoid B039 (mutable default)
_output_dir_var: ContextVar[Path | None] = ContextVar("output_dir", default=None)
_shutdown_event_var: ContextVar[asyncio.Event | None] = ContextVar("shutdown_event", default=None)


def get_output_dir() -> Path:
    """Get the current output directory from context."""
    value = _output_dir_var.get()
    return value if value is not None else Path.cwd()


def set_output_dir(path: Path) -> None:
    """Set the output directory in the current context."""
    _output_dir_var.set(path)


def get_shutdown_event() -> asyncio.Event | None:
    """Get the shutdown event from context."""
    return _shutdown_event_var.get()


def set_shutdown_event(event: asyncio.Event | None) -> None:
    """Set the shutdown event in the current context."""
    _shutdown_event_var.set(event)


class GitHubConfigModel(BaseModel):
    """GitHub configuration."""

    enabled: bool = False
    repo_url: str = ""
    create_repo: bool = True
    yolo_mode: bool = False
    token_configured: bool = False


class ProjectConfig(BaseModel):
    """Project configuration from form submission."""

    name: str
    platforms: list[str]
    user_story: dict[str, str]  # role, action, outcome
    features: list[str]
    tech_stack: dict[str, list[str]]  # frontend, backend, database, tools
    aesthetics: list[str]
    github: GitHubConfigModel | None = None

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: list[str]) -> list[str]:
        """Validate features list constraints."""
        if not v:
            raise ValueError("At least one feature is required")
        if len(v) > 20:
            raise ValueError("Maximum 20 features allowed")

        for i, feature in enumerate(v):
            if len(feature) > 2000:
                raise ValueError(f"Feature {i + 1} exceeds 2000 character limit")
            if not feature.strip():
                raise ValueError(f"Feature {i + 1} cannot be empty")

        return v


class GitHubTokenRequest(BaseModel):
    """Request to validate and store GitHub token."""

    token: str


class CostEstimate(BaseModel):
    """Cost estimate response."""

    min_cost: float
    max_cost: float
    breakdown: dict[str, float]


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/config")
async def get_config() -> dict[str, Any]:
    """Get current configuration (safe fields only)."""
    config = ConfigManager()
    return {
        "has_api_key": bool(config.get_api_key()),
        "model": config.get("api.model"),
        "cost_limit": config.get("preferences.cost_limit"),
    }


@app.post("/api/github/validate-token")
async def validate_github_token(request: GitHubTokenRequest) -> dict[str, Any]:
    """Validate and store a GitHub token."""
    try:
        github = GitHubService(token=request.token)
        user_info = github.validate_token()

        # Store the token securely
        GitHubService.set_token(request.token)

        return {
            "valid": True,
            "username": user_info.get("login"),
            "message": "Token validated and stored successfully",
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Token validation failed: {e}",
        }


@app.get("/api/github/status")
async def github_status() -> dict[str, Any]:
    """Check GitHub token status."""
    token = GitHubService.get_token()
    if not token:
        return {"configured": False}

    try:
        github = GitHubService(token=token)
        user_info = github.validate_token()
        return {
            "configured": True,
            "username": user_info.get("login"),
        }
    except Exception:
        return {"configured": False, "error": "Token invalid or expired"}


@app.post("/api/estimate")
async def estimate_cost(config: ProjectConfig) -> CostEstimate:
    """Estimate the cost for project generation."""
    # Base costs per step (in dollars)
    step_costs = {
        "product_spec": (0.10, 0.30),
        "structure": (0.05, 0.10),
        "documentation": (0.15, 0.40),
        "tooling": (0.10, 0.25),
        "demo_code": (0.80, 2.00),
    }

    # Adjust based on complexity
    feature_multiplier = 1 + (len(config.features) - 1) * 0.1
    platform_multiplier = 1 + (len(config.platforms) - 1) * 0.15

    total_min = 0.0
    total_max = 0.0
    breakdown = {}

    for step, (min_cost, max_cost) in step_costs.items():
        adjusted_min = min_cost * feature_multiplier * platform_multiplier
        adjusted_max = max_cost * feature_multiplier * platform_multiplier
        breakdown[step] = (adjusted_min + adjusted_max) / 2
        total_min += adjusted_min
        total_max += adjusted_max

    return CostEstimate(
        min_cost=round(total_min, 2),
        max_cost=round(total_max, 2),
        breakdown=breakdown,
    )


@app.websocket("/ws/generate")
async def generate_project(websocket: WebSocket) -> None:
    """WebSocket endpoint for project generation with progress updates.

    Issue #11 Fix: Properly handle JSON parse errors and validation errors
    instead of crashing the WebSocket connection.
    """
    await websocket.accept()

    try:
        # Receive project configuration
        data = await websocket.receive_text()

        # Issue #11 Fix: Handle JSON parse errors gracefully
        try:
            config_data = json.loads(data)
        except json.JSONDecodeError as e:
            await websocket.send_json({"type": "error", "message": f"Invalid JSON: {e.msg}"})
            return

        # Issue #11 Fix: Handle validation errors gracefully
        try:
            project_config = ProjectConfig(**config_data)
        except ValidationError as e:
            await websocket.send_json({"type": "error", "message": f"Invalid configuration: {e}"})
            return

        # Create orchestrator using context variable for output dir
        orchestrator = GenerationOrchestrator(
            output_dir=get_output_dir(),
            project_name=project_config.name,
        )

        # Progress callback
        async def send_progress(step: str, status: str, details: dict | None = None) -> None:
            await websocket.send_json(
                {
                    "type": "progress",
                    "step": step,
                    "status": status,
                    "details": details or {},
                }
            )

        # Run generation
        result = await orchestrator.generate(
            platforms=project_config.platforms,
            user_story=project_config.user_story,
            features=project_config.features,
            tech_stack=project_config.tech_stack,
            aesthetics=project_config.aesthetics,
            progress_callback=send_progress,
        )

        # Send completion
        await websocket.send_json(
            {
                "type": "complete",
                "result": {
                    "path": str(result["path"]),
                    "total_cost": result["total_cost"],
                    "generation_time": result["generation_time"],
                },
            }
        )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json(
            {
                "type": "error",
                "message": str(e),
            }
        )


def start_server(port: int = 8765, output_dir: Path | None = None) -> None:
    """Start the FastAPI server."""
    # Issue #10 Fix: Use context variables instead of global state
    if output_dir:
        set_output_dir(output_dir)

    set_shutdown_event(asyncio.Event())

    # Mount static files for the frontend
    frontend_dir = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="static")

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


@app.get("/")
async def serve_frontend() -> FileResponse:
    """Serve the frontend index.html."""
    frontend_dir = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return FileResponse(Path(__file__).parent / "fallback.html")
