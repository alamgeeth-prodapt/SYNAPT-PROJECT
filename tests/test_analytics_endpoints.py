"""
Tests for Disruption Analytics & Reporting Router (/api/v1/analytics).
Validates unauthenticated rejection, full aggregated overview, filter application, and data invariants.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_analytics_unauthenticated():
    """Verify that requests without JWT token are rejected with 401."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 401


def test_analytics_overview_structure(auth_headers):
    """Verify that /api/v1/analytics/overview returns all expected keys and aggregations."""
    response = client.get("/api/v1/analytics/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # 1. KPIs
    assert "kpis" in data
    kpis = data["kpis"]
    assert kpis["total_incidents"] == 100000
    assert kpis["avg_production_impact_pct"] > 0
    assert kpis["avg_revenue_loss_usd"] > 0
    assert kpis["total_revenue_loss_usd"] > 0
    assert kpis["avg_recovery_days"] > 0
    assert kpis["avg_resilience_score"] > 0
    assert 0 <= kpis["backup_supplier_pct"] <= 100
    assert kpis["p1_critical_count"] > 0

    # 2. Disruption Type Distribution
    assert "disruption_type_distribution" in data
    assert len(data["disruption_type_distribution"]) == 6
    types = [d["disruption_type"] for d in data["disruption_type_distribution"]]
    assert "Cyber Attack" in types
    assert "Factory Incident" in types

    # 3. Industry Exposure
    assert "industry_exposure" in data
    assert len(data["industry_exposure"]) == 5
    industries = [d["industry"] for d in data["industry_exposure"]]
    assert "Electronics" in industries
    assert "Automotive" in industries

    # 4. Severity vs Backup Comparison
    assert "severity_backup_comparison" in data
    assert len(data["severity_backup_comparison"]) > 0

    # 5. Regional Breakdown
    assert "regional_breakdown" in data
    assert len(data["regional_breakdown"]) == 5

    # 6. Response Strategy Effectiveness
    assert "response_effectiveness" in data
    assert len(data["response_effectiveness"]) == 5

    # 7. Triage Distribution
    assert "triage_distribution" in data
    assert len(data["triage_distribution"]) == 4
    triages = [t["prioritization_level"] for t in data["triage_distribution"]]
    assert "P1-Critical" in triages


def test_analytics_filtered_by_industry(auth_headers):
    """Verify that filtering by industry correctly filters the results."""
    response = client.get("/api/v1/analytics/overview?industry=Electronics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["applied_filters"]["industry"] == "Electronics"
    # Filtered incidents should be less than 100,000 but > 0
    assert 0 < data["kpis"]["total_incidents"] < 100000
    assert len(data["industry_exposure"]) == 1
    assert data["industry_exposure"][0]["industry"] == "Electronics"
