"""
Phase 5 Quality & Evaluation Test Suite.
Validates JWT Authentication, all FastAPI endpoints, multi-agent contracts, TreeSHAP, and SQL builder.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["total_records"] == 100000
    assert len(data["models_loaded"]) == 3


def test_auth_login_json_success():
    """Verify login with seeded admin / admin credentials via JSON endpoint."""
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"


def test_auth_login_oauth2_success():
    """Verify OAuth2 password form flow for Swagger UI padlock button."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_auth_login_invalid_credentials():
    """Verify 401 on bad credentials."""
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.fixture(scope="module")
def auth_headers():
    """Fixture providing a valid JWT Bearer header for protected endpoint tests."""
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "admin"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_protected_route_unauthenticated():
    """Verify that requests without token are rejected with 401 Unauthorized."""
    payload = {
        "disruption_type": "Port Congestion",
        "industry": "Consumer Goods",
        "supplier_tier": 1,
        "supplier_region": "North America",
        "supplier_size": "Medium",
        "has_backup_supplier": True,
        "disruption_severity": 1,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 401


def test_get_current_user_profile(auth_headers):
    """Verify /api/v1/auth/me returns the authenticated user."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_orchestrate_severe_incident(auth_headers):
    payload = {
        "disruption_type": "Cyber Attack",
        "industry": "Electronics",
        "supplier_tier": 2,
        "supplier_region": "Asia-Pacific",
        "supplier_size": "Large",
        "has_backup_supplier": False,
        "disruption_severity": 4,
    }
    response = client.post("/api/v1/orchestrate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "dossier_id" in data
    assert data["impact"]["prioritization_level"] == "P1-Critical"
    assert data["impact"]["predicted_production_impact_pct"] > 40.0
    assert data["impact"]["resilience_score"] < 50.0
    assert data["judge_verdict"]["status"] in ("APPROVED", "FLAGGED_FOR_HUMAN_REVIEW")
    assert len(data["investigation"]["analog_cases"]) > 0


def test_predict_endpoint(auth_headers):
    payload = {
        "disruption_type": "Port Congestion",
        "industry": "Consumer Goods",
        "supplier_tier": 1,
        "supplier_region": "North America",
        "supplier_size": "Medium",
        "has_backup_supplier": True,
        "disruption_severity": 1,
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["prioritization_level"] in ("P3-Medium", "P4-Low")
    assert data["resilience_score"] > 70.0


def test_explain_endpoint_shap(auth_headers):
    payload = {
        "disruption_type": "Factory Incident",
        "industry": "Automotive",
        "supplier_tier": 1,
        "supplier_region": "Europe",
        "supplier_size": "Large",
        "has_backup_supplier": False,
        "disruption_severity": 3,
    }
    response = client.post("/api/v1/explain?target=revenue_loss_usd", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "base_value" in data
    assert "predicted_value" in data
    assert "features" in data
    assert len(data["top_risk_drivers"]) > 0


def test_query_sql_endpoint(auth_headers):
    payload = {
        "query": "Show me factory fire disruptions in Automotive without backup supplier",
        "limit": 3,
    }
    response = client.post("/api/v1/query-sql", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "SELECT" in data["generated_sql"].upper()
    assert "v_disruption_details" in data["generated_sql"]
    assert data["row_count"] > 0
    assert len(data["records"]) <= 3


def test_human_feedback(auth_headers):
    payload = {
        "dossier_id": "DOS-TEST-12345",
        "operator_id": "auditor_lead",
        "rating": 5,
        "accepted_strategy": True,
        "comments": "Audited and verified against procurement lead-time guidelines.",
    }
    response = client.post("/api/v1/feedback", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"
