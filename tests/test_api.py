"""API endpoint tests."""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert data["version"] == "0.1.0"
        assert "database" in data

    def test_health_check_response_structure(self, client):
        """Test health check response has correct structure."""
        response = client.get("/health")
        data = response.json()

        required_fields = ["status", "timestamp", "version", "database"]
        for field in required_fields:
            assert field in data


class TestPlannerEndpoints:
    """Tests for planning endpoints."""

    @pytest.fixture
    def valid_plan_request(self):
        """Valid plan request payload."""
        return {
            "context": "Need to prepare for product launch",
            "goals": [
                "Complete marketing materials",
                "Setup infrastructure",
                "Train support team",
            ],
            "constraints": ["Launch date is next Friday", "Limited budget"],
        }

    def test_create_weekly_plan_success(self, client, valid_plan_request):
        """Test successful weekly plan creation."""
        response = client.post("/plan/week", json=valid_plan_request)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "plan_id" in data
        assert "tasks" in data
        assert "summary" in data
        assert "created_at" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) > 0

    def test_create_daily_plan_success(self, client, valid_plan_request):
        """Test successful daily plan creation."""
        response = client.post("/plan/today", json=valid_plan_request)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "plan_id" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_plan_validation_empty_context(self, client):
        """Test plan request fails with empty context."""
        invalid_request = {
            "context": "",
            "goals": ["Goal 1"],
        }
        response = client.post("/plan/week", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_plan_validation_empty_goals(self, client):
        """Test plan request fails with empty goals list."""
        invalid_request = {
            "context": "Some context",
            "goals": [],
        }
        response = client.post("/plan/week", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_plan_validation_missing_required_fields(self, client):
        """Test plan request fails with missing required fields."""
        invalid_request = {
            "context": "Some context",
        }
        response = client.post("/plan/week", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_task_structure_in_response(self, client, valid_plan_request):
        """Test that tasks in response have correct structure."""
        response = client.post("/plan/week", json=valid_plan_request)
        data = response.json()

        if len(data["tasks"]) > 0:
            task = data["tasks"][0]
            required_fields = [
                "id",
                "title",
                "priority",
                "status",
                "created_at",
                "updated_at",
            ]
            for field in required_fields:
                assert field in task
