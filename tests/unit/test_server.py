"""Tests for FastAPI server endpoints."""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from specinit.server.app import (
    ProjectConfig,
    app,
    get_output_dir,
    get_shutdown_event,
    set_output_dir,
    set_shutdown_event,
)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def _mock_config_manager():
    """Mock ConfigManager for tests."""
    with patch("specinit.server.app.ConfigManager") as mock:
        instance = MagicMock()
        instance.get_api_key.return_value = "sk-ant-test-key"
        instance.get.side_effect = lambda key: {
            "api.model": "claude-sonnet-4-5-20250929",
            "preferences.cost_limit": 5.00,
        }.get(key)
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_github_service():
    """Mock GitHubService for tests."""
    with patch("specinit.server.app.GitHubService") as mock:
        yield mock


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Should return healthy status."""
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestConfigEndpoint:
    """Tests for /api/config endpoint."""

    def test_get_config_with_api_key(self, client, _mock_config_manager):
        """Should return config with has_api_key true when key exists."""
        response = client.get("/api/config")

        assert response.status_code == 200
        data = response.json()
        assert data["has_api_key"] is True
        assert data["model"] == "claude-sonnet-4-5-20250929"
        assert data["cost_limit"] == 5.00

    def test_get_config_without_api_key(self, client):
        """Should return config with has_api_key false when no key."""
        with patch("specinit.server.app.ConfigManager") as mock:
            instance = MagicMock()
            instance.get_api_key.return_value = None
            instance.get.return_value = None
            mock.return_value = instance

            response = client.get("/api/config")

            assert response.status_code == 200
            assert response.json()["has_api_key"] is False


class TestGitHubValidateToken:
    """Tests for /api/github/validate-token endpoint."""

    def test_validate_token_success(self, client, mock_github_service):
        """Should validate and store token on success."""
        instance = MagicMock()
        instance.validate_token.return_value = {"login": "testuser"}
        mock_github_service.return_value = instance

        response = client.post(
            "/api/github/validate-token",
            json={"token": "ghp_testtoken123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "testuser"
        assert "Token validated" in data["message"]
        mock_github_service.set_token.assert_called_once_with("ghp_testtoken123")

    def test_validate_token_failure(self, client, mock_github_service):
        """Should return error on invalid token."""
        instance = MagicMock()
        instance.validate_token.side_effect = Exception("Invalid token")
        mock_github_service.return_value = instance

        response = client.post(
            "/api/github/validate-token",
            json={"token": "invalid-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Invalid token" in data["message"]


class TestGitHubStatus:
    """Tests for /api/github/status endpoint."""

    def test_github_status_not_configured(self, client, mock_github_service):
        """Should return not configured when no token."""
        mock_github_service.get_token.return_value = None

        response = client.get("/api/github/status")

        assert response.status_code == 200
        assert response.json()["configured"] is False

    def test_github_status_configured_valid(self, client, mock_github_service):
        """Should return configured with username when token valid."""
        mock_github_service.get_token.return_value = "ghp_validtoken"
        instance = MagicMock()
        instance.validate_token.return_value = {"login": "validuser"}
        mock_github_service.return_value = instance

        response = client.get("/api/github/status")

        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is True
        assert data["username"] == "validuser"

    def test_github_status_configured_invalid(self, client, mock_github_service):
        """Should return not configured with error when token invalid."""
        mock_github_service.get_token.return_value = "ghp_expiredtoken"
        instance = MagicMock()
        instance.validate_token.side_effect = Exception("Token expired")
        mock_github_service.return_value = instance

        response = client.get("/api/github/status")

        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is False
        assert "error" in data


class TestCostEstimate:
    """Tests for /api/estimate endpoint."""

    def test_estimate_cost_single_feature_single_platform(self, client):
        """Should return cost estimate for simple project."""
        response = client.post(
            "/api/estimate",
            json={
                "name": "test-project",
                "platforms": ["web"],
                "user_story": {
                    "role": "developer",
                    "action": "build apps",
                    "outcome": "save time",
                },
                "features": ["Feature 1"],
                "tech_stack": {
                    "frontend": ["React"],
                    "backend": ["FastAPI"],
                    "database": [],
                    "tools": [],
                },
                "aesthetics": ["minimalist"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "min_cost" in data
        assert "max_cost" in data
        assert "breakdown" in data
        assert data["min_cost"] > 0
        assert data["max_cost"] > data["min_cost"]

    def test_estimate_cost_increases_with_features(self, client):
        """Should increase cost with more features."""
        base_config = {
            "name": "test-project",
            "platforms": ["web"],
            "user_story": {
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            "tech_stack": {
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            "aesthetics": [],
        }

        # Single feature
        response1 = client.post(
            "/api/estimate",
            json={**base_config, "features": ["Feature 1"]},
        )
        cost1 = response1.json()["max_cost"]

        # Multiple features
        response2 = client.post(
            "/api/estimate",
            json={**base_config, "features": ["Feature 1", "Feature 2", "Feature 3"]},
        )
        cost2 = response2.json()["max_cost"]

        assert cost2 > cost1

    def test_estimate_cost_increases_with_platforms(self, client):
        """Should increase cost with more platforms."""
        base_config = {
            "name": "test-project",
            "features": ["Feature 1"],
            "user_story": {
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            "tech_stack": {
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            "aesthetics": [],
        }

        # Single platform
        response1 = client.post(
            "/api/estimate",
            json={**base_config, "platforms": ["web"]},
        )
        cost1 = response1.json()["max_cost"]

        # Multiple platforms
        response2 = client.post(
            "/api/estimate",
            json={**base_config, "platforms": ["web", "ios", "android"]},
        )
        cost2 = response2.json()["max_cost"]

        assert cost2 > cost1


class TestServeFrontend:
    """Tests for / endpoint."""

    def test_serve_frontend_fallback(self, client):
        """Should serve fallback when frontend not built."""
        with patch("specinit.server.app.Path") as mock_path:
            # Make frontend dir not exist
            mock_instance = MagicMock()
            mock_instance.exists.return_value = False
            mock_path.return_value = mock_instance

            # The endpoint will try to serve index.html which won't exist
            # This is expected behavior - it will return 404 or serve fallback
            response = client.get("/")
            # We just verify it doesn't crash
            assert response.status_code in [200, 404]


class TestWebSocketJSONParsing:
    """Tests for WebSocket JSON error handling (Issue #11 fix)."""

    def test_websocket_rejects_malformed_json(self, client):
        """WebSocket should return error for malformed JSON."""
        with client.websocket_connect("/ws/generate") as websocket:
            # Send malformed JSON
            websocket.send_text("not valid json {{{")

            # Should receive error message, not crash
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "Invalid JSON" in response["message"] or "JSON" in response["message"]

    def test_websocket_rejects_invalid_config(self, client):
        """WebSocket should return error for invalid config structure."""
        with client.websocket_connect("/ws/generate") as websocket:
            # Send valid JSON but invalid config (missing required fields)
            websocket.send_text('{"invalid": "config"}')

            # Should receive error message about validation
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "message" in response


class TestContextVariables:
    """Tests for context variable helpers (Issue #10 fix)."""

    def test_get_output_dir_returns_cwd_by_default(self):
        """get_output_dir should return cwd when not set."""
        result = get_output_dir()
        assert result == Path.cwd()

    def test_set_and_get_output_dir(self):
        """set_output_dir should store value retrievable by get_output_dir."""
        test_path = Path("/tmp/test-project")
        set_output_dir(test_path)

        result = get_output_dir()
        assert result == test_path

    def test_get_shutdown_event_returns_none_by_default(self):
        """get_shutdown_event should return None when not set."""
        # Reset by setting to None first
        set_shutdown_event(None)

        result = get_shutdown_event()
        assert result is None

    def test_set_and_get_shutdown_event(self):
        """set_shutdown_event should store value retrievable by get_shutdown_event."""
        event = asyncio.Event()
        set_shutdown_event(event)

        result = get_shutdown_event()
        assert result is event


class TestFeatureValidation:
    """Tests for feature validation in ProjectConfig (Issue #24)."""

    def test_valid_features_accepted(self):
        """ProjectConfig should accept valid features."""
        config = ProjectConfig(
            name="test",
            platforms=["web"],
            user_story={"role": "user", "action": "test", "outcome": "works"},
            features=["Feature 1", "Feature 2"],
            tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
            aesthetics=[],
        )
        assert len(config.features) == 2

    def test_rejects_empty_feature_string(self):
        """ProjectConfig should reject empty feature strings."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                name="test",
                platforms=["web"],
                user_story={"role": "user", "action": "test", "outcome": "works"},
                features=["Feature 1", ""],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
            )
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_rejects_whitespace_only_feature(self):
        """ProjectConfig should reject features with only whitespace."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                name="test",
                platforms=["web"],
                user_story={"role": "user", "action": "test", "outcome": "works"},
                features=["Feature 1", "   "],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
            )
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_rejects_more_than_20_features(self):
        """ProjectConfig should reject more than 20 features."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                name="test",
                platforms=["web"],
                user_story={"role": "user", "action": "test", "outcome": "works"},
                features=[f"Feature {i}" for i in range(21)],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
            )
        assert "maximum 20 features" in str(exc_info.value).lower()

    def test_rejects_feature_exceeding_2000_chars(self):
        """ProjectConfig should reject features exceeding 2000 characters."""
        long_feature = "a" * 2001

        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                name="test",
                platforms=["web"],
                user_story={"role": "user", "action": "test", "outcome": "works"},
                features=["Feature 1", long_feature],
                tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
                aesthetics=[],
            )
        assert "2000 character limit" in str(exc_info.value).lower()

    def test_accepts_exactly_20_features(self):
        """ProjectConfig should accept exactly 20 features."""
        config = ProjectConfig(
            name="test",
            platforms=["web"],
            user_story={"role": "user", "action": "test", "outcome": "works"},
            features=[f"Feature {i}" for i in range(20)],
            tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
            aesthetics=[],
        )
        assert len(config.features) == 20

    def test_accepts_feature_exactly_2000_chars(self):
        """ProjectConfig should accept features at exactly 2000 characters."""
        max_length_feature = "a" * 2000

        config = ProjectConfig(
            name="test",
            platforms=["web"],
            user_story={"role": "user", "action": "test", "outcome": "works"},
            features=["Feature 1", max_length_feature],
            tech_stack={"frontend": [], "backend": [], "database": [], "tools": []},
            aesthetics=[],
        )
        assert len(config.features[1]) == 2000


class TestAdditionalContext:
    """Tests for optional additional_context field (Issue #22)."""

    def test_project_config_accepts_additional_context(self):
        """ProjectConfig should accept optional additional_context field."""
        config = ProjectConfig(
            name="test-project",
            platforms=["web"],
            user_story={
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            features=["Feature 1"],
            tech_stack={
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            aesthetics=["minimalist"],
            additional_context="This is additional context for the project generation.",
        )

        assert config.additional_context == "This is additional context for the project generation."

    def test_project_config_additional_context_is_optional(self):
        """ProjectConfig should work without additional_context field."""
        config = ProjectConfig(
            name="test-project",
            platforms=["web"],
            user_story={
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            features=["Feature 1"],
            tech_stack={
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            aesthetics=["minimalist"],
        )

        assert config.additional_context is None

    def test_cost_estimate_accepts_additional_context(self, client):
        """Cost estimate endpoint should accept additional_context."""
        response = client.post(
            "/api/estimate",
            json={
                "name": "test-project",
                "platforms": ["web"],
                "user_story": {
                    "role": "developer",
                    "action": "build apps",
                    "outcome": "save time",
                },
                "features": ["Feature 1"],
                "tech_stack": {
                    "frontend": ["React"],
                    "backend": ["FastAPI"],
                    "database": [],
                    "tools": [],
                },
                "aesthetics": ["minimalist"],
                "additional_context": "Detailed requirements and constraints.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "min_cost" in data
        assert "max_cost" in data

    def test_websocket_accepts_additional_context(self, client):
        """WebSocket should accept additional_context in config."""
        with patch("specinit.server.app.GenerationOrchestrator") as mock_orchestrator:
            mock_instance = MagicMock()
            mock_orchestrator.return_value = mock_instance

            async def mock_generate(**_kwargs):
                return {
                    "path": Path("/tmp/test-project"),
                    "total_cost": 1.50,
                    "generation_time": 30.0,
                }

            mock_instance.generate.side_effect = mock_generate

            with client.websocket_connect("/ws/generate") as websocket:
                websocket.send_json(
                    {
                        "name": "test-project",
                        "platforms": ["web"],
                        "user_story": {
                            "role": "developer",
                            "action": "build apps",
                            "outcome": "save time",
                        },
                        "features": ["Feature 1"],
                        "tech_stack": {
                            "frontend": ["React"],
                            "backend": ["FastAPI"],
                            "database": [],
                            "tools": [],
                        },
                        "aesthetics": ["minimalist"],
                        "additional_context": "Additional project context",
                    }
                )

                response = websocket.receive_json()
                # Should not error - should process successfully
                assert response["type"] in ["progress", "complete"]


class TestProjectDescription:
    """Tests for project_description field (Issue #35)."""

    def test_project_config_accepts_project_description(self):
        """ProjectConfig should accept optional project_description field."""
        config = ProjectConfig(
            name="test-project",
            project_description="A mobile app for tracking daily research notes",
            platforms=["web"],
            user_story={
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            features=["Feature 1"],
            tech_stack={
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            aesthetics=["minimalist"],
        )
        assert config.project_description == "A mobile app for tracking daily research notes"

    def test_project_config_project_description_is_optional(self):
        """ProjectConfig should work without project_description field."""
        config = ProjectConfig(
            name="test-project",
            platforms=["web"],
            user_story={
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            features=["Feature 1"],
            tech_stack={
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            aesthetics=["minimalist"],
        )
        assert config.project_description is None

    def test_rejects_project_description_exceeding_500_chars(self):
        """ProjectConfig should reject project_description exceeding 500 characters."""
        long_description = "a" * 501

        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                name="test-project",
                project_description=long_description,
                platforms=["web"],
                user_story={
                    "role": "developer",
                    "action": "build apps",
                    "outcome": "save time",
                },
                features=["Feature 1"],
                tech_stack={
                    "frontend": ["React"],
                    "backend": ["FastAPI"],
                    "database": [],
                    "tools": [],
                },
                aesthetics=["minimalist"],
            )
        assert "500" in str(exc_info.value).lower()

    def test_accepts_project_description_exactly_500_chars(self):
        """ProjectConfig should accept project_description at exactly 500 characters."""
        max_length_description = "a" * 500

        config = ProjectConfig(
            name="test-project",
            project_description=max_length_description,
            platforms=["web"],
            user_story={
                "role": "developer",
                "action": "build apps",
                "outcome": "save time",
            },
            features=["Feature 1"],
            tech_stack={
                "frontend": ["React"],
                "backend": ["FastAPI"],
                "database": [],
                "tools": [],
            },
            aesthetics=["minimalist"],
        )
        assert len(config.project_description) == 500


class TestSuggestEndpoint:
    """Tests for /api/suggest endpoint (Issue #37)."""

    def test_suggest_user_stories_success(self, client, _mock_config_manager):
        """Should return user story suggestions given project description."""
        with patch("specinit.server.app.Anthropic") as mock_anthropic:
            # Mock Claude API response
            mock_message = MagicMock()
            mock_message.content = [
                MagicMock(
                    text="As a researcher, I want to create daily notes, so that I can document my progress\nAs a researcher, I want to tag notes by project, so that I can organize my work\nAs a researcher, I want to search past notes, so that I can find information"
                )
            ]
            mock_message.usage = MagicMock(input_tokens=450, output_tokens=180)
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            response = client.post(
                "/api/suggest",
                json={
                    "field": "user_stories",
                    "context": {
                        "project_name": "ResearchNotes",
                        "project_description": "A mobile app for tracking daily research notes",
                        "platforms": ["iOS", "Android"],
                    },
                    "count": 3,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "suggestions" in data
            assert "cost" in data
            assert "tokens_used" in data
            assert len(data["suggestions"]) == 3
            assert isinstance(data["cost"], float)
            assert data["cost"] > 0
            assert data["tokens_used"]["input"] == 450
            assert data["tokens_used"]["output"] == 180

    def test_suggest_features_success(self, client, _mock_config_manager):
        """Should return feature suggestions given user story."""
        with patch("specinit.server.app.Anthropic") as mock_anthropic:
            mock_message = MagicMock()
            mock_message.content = [
                MagicMock(
                    text="Rich text editor for notes\nDate-based organization\nTag management\nSearch functionality"
                )
            ]
            mock_message.usage = MagicMock(input_tokens=500, output_tokens=150)
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            response = client.post(
                "/api/suggest",
                json={
                    "field": "features",
                    "context": {
                        "project_name": "ResearchNotes",
                        "userStory": {
                            "role": "researcher",
                            "action": "create daily notes",
                            "outcome": "document progress",
                        },
                    },
                    "count": 4,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["suggestions"]) == 4

    def test_suggest_tech_stack_success(self, client, _mock_config_manager):
        """Should return tech stack suggestions given features and platforms."""
        with patch("specinit.server.app.Anthropic") as mock_anthropic:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="React Native\nExpo\nFastAPI\nSQLite")]
            mock_message.usage = MagicMock(input_tokens=600, output_tokens=100)
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            response = client.post(
                "/api/suggest",
                json={
                    "field": "tech_stack",
                    "context": {
                        "platforms": ["iOS", "Android"],
                        "features": ["Rich text editor", "Search"],
                    },
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["suggestions"]) > 0

    def test_suggest_without_api_key_fails(self, client):
        """Should return error when API key is not configured."""
        with patch("specinit.server.app.ConfigManager") as mock:
            instance = MagicMock()
            instance.get_api_key.return_value = None
            mock.return_value = instance

            response = client.post(
                "/api/suggest",
                json={
                    "field": "user_stories",
                    "context": {"project_description": "A test app"},
                },
            )

            assert response.status_code == 401
            data = response.json()
            assert "API key" in data["detail"]

    def test_suggest_invalid_field_fails(self, client, _mock_config_manager):
        """Should return 400 for unsupported field types."""
        response = client.post(
            "/api/suggest",
            json={
                "field": "invalid_field",
                "context": {},
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "not supported" in data["detail"].lower()

    def test_suggest_with_count_parameter(self, client, _mock_config_manager):
        """Should respect count parameter (1-10)."""
        with patch("specinit.server.app.Anthropic") as mock_anthropic:
            mock_message = MagicMock()
            mock_message.content = [
                MagicMock(
                    text="Suggestion 1\nSuggestion 2\nSuggestion 3\nSuggestion 4\nSuggestion 5"
                )
            ]
            mock_message.usage = MagicMock(input_tokens=400, output_tokens=120)
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            response = client.post(
                "/api/suggest",
                json={
                    "field": "features",
                    "context": {},
                    "count": 5,
                },
            )

            assert response.status_code == 200
            assert len(response.json()["suggestions"]) == 5

    def test_suggest_validates_count_range(self, client, _mock_config_manager):
        """Should reject count outside 1-10 range."""
        # Test count > 10
        response = client.post(
            "/api/suggest",
            json={
                "field": "features",
                "context": {},
                "count": 11,
            },
        )
        assert response.status_code == 422  # Pydantic validation error

        # Test count < 1
        response = client.post(
            "/api/suggest",
            json={
                "field": "features",
                "context": {},
                "count": 0,
            },
        )
        assert response.status_code == 422

    def test_suggest_uses_current_value_to_refine(self, client, _mock_config_manager):
        """Should include current_value in prompt to refine suggestions."""
        with patch("specinit.server.app.Anthropic") as mock_anthropic:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Advanced search\nFull-text search")]
            mock_message.usage = MagicMock(input_tokens=400, output_tokens=80)
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            response = client.post(
                "/api/suggest",
                json={
                    "field": "features",
                    "context": {},
                    "current_value": "search",
                    "count": 2,
                },
            )

            assert response.status_code == 200
            # Verify that the create call was made
            mock_client.messages.create.assert_called_once()

    def test_suggest_handles_api_timeout(self, client, _mock_config_manager):
        """Should return 408 when Claude API times out."""
        with patch("specinit.server.app.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = TimeoutError("API timeout")
            mock_anthropic.return_value = mock_client

            response = client.post(
                "/api/suggest",
                json={
                    "field": "features",
                    "context": {},
                },
            )

            assert response.status_code == 408
            data = response.json()
            assert "timeout" in data["detail"].lower()
