"""FastAPI server for SpecInit web interface."""

import asyncio
import json
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

# Global state
_output_dir: Path = Path.cwd()
_shutdown_event: asyncio.Event | None = None


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
    """WebSocket endpoint for project generation with progress updates."""
    await websocket.accept()

    try:
        # Receive project configuration
        data = await websocket.receive_text()
        config_data = json.loads(data)
        project_config = ProjectConfig(**config_data)

        # Create orchestrator
        orchestrator = GenerationOrchestrator(
            output_dir=_output_dir,
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
    global _output_dir, _shutdown_event  # noqa: PLW0603

    if output_dir:
        _output_dir = output_dir

    _shutdown_event = asyncio.Event()

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
