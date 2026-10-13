"""
Integration and Unit Tests for Executive AI Copilot Two-Agent Service.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


def test_copilot_status(auth_headers):
    """Verifies that copilot status reports engine, framework, models, and multi-agent configuration."""
    response = client.get("/api/v1/copilot/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "engine" in data
    assert "agents" in data
    assert len(data["agents"]) >= 2
    assert any("Agent 1: Intelligence Drafting Analyst" in a["name"] for a in data["agents"])
    assert any("Agent 2: Senior Audit Reviewer" in a["name"] for a in data["agents"])
    assert "framework" in data
    assert "models" in data
    assert data["models"]["drafter"] == "gemini-3.5-flash-lite"
    assert data["models"]["reviewer"] == "gemini-3.5-flash-lite"


def test_copilot_chat_workflow(auth_headers):
    """Verifies end-to-end 2-agent pipeline returns grounded SQL, 400-500 word report, and review audit."""
    payload = {
        "query": "What is the impact and optimal response strategy for cyber attacks on automotive suppliers in Europe?",
        "include_ml": True,
        "limit": 10,
    }
    response = client.post("/api/v1/copilot/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # 1. SQL generation check
    assert "sql_query" in data
    assert "v_disruption_details" in data["sql_query"]
    assert "Cyber Attack" in data["sql_query"]
    assert "Automotive" in data["sql_query"]

    # 2. Retrieved rows check
    assert data["data_summary"]["row_count"] > 0

    # 3. Two-Agent Trace check
    trace = data["agent_trace"]
    assert trace["drafter"]["agent_name"] == "Agent 1: Intelligence Drafting Analyst"
    assert trace["reviewer"]["agent_name"] == "Agent 2: Senior Audit Reviewer"
    assert trace["reviewer"]["status"] == "APPROVED"
    assert trace["reviewer"]["quality_score"] >= 9.0

    # 4. Word count check (must be comprehensive report, 250+ words target)
    word_count = data["word_count"]
    assert word_count >= 250

    # 5. Report structure check
    report = data["final_report"]
    assert "Executive Intelligence Memorandum" in report
    assert any(h.lower() in report.lower() for h in ["findings", "data", "warehouse", "impact", "empirical"])
    assert any(h.lower() in report.lower() for h in ["governance", "mitigation", "strategic", "playbook", "actions"])


def test_copilot_sop_intent_routing(auth_headers):
    """Verifies that SOP questions route to the SOP Agent and return structured chunk blocks."""
    payload = {
        "query": "What is the SOP procedure and playbook checklist for cyber attack containment?",
        "include_ml": False,
        "limit": 5,
    }
    response = client.post("/api/v1/copilot/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "sop"
    assert any("SOP Agent" in a for a in data["activated_agents"])
    assert data["sop_data"] is not None
    assert "chunks" in data["sop_data"] or "playbook_title" in data["sop_data"]
    assert data["sop_data"].get("tool_used") in ["trident_get_procedures", "trident_query"]


def test_copilot_unauthenticated():
    """Verifies that unauthenticated requests to copilot are rejected with 401."""
    response = client.post("/api/v1/copilot/chat", json={"query": "test query"})
    assert response.status_code == 401


def test_copilot_gemini_provider_detection(auth_headers, monkeypatch):
    """Verifies that GEMINI_API_KEY environment configuration switches provider to Google Gemini."""
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyMockKeyForTesting12345")
    response = client.get("/api/v1/copilot/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "google_gemini"
    assert data["engine"] == "google_gemini"
    assert data["live_llm_available"] is True
    assert "Google Gemini" in data["primary_llm"]


def test_copilot_anthropic_provider_detection(auth_headers, monkeypatch):
    """Verifies fallback to Anthropic Claude when GEMINI_API_KEY is unset and ANTHROPIC_API_KEY is provided."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-mock-key-12345")
    response = client.get("/api/v1/copilot/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "anthropic_claude"
    assert data["engine"] == "anthropic_claude"
    assert data["live_llm_available"] is True
    assert "Anthropic Claude" in data["primary_llm"]


def test_copilot_general_conversational_routing(auth_headers):
    """Verifies that unclassified casual queries route directly to CrewAI without invoking SQL or SOP workers."""
    payload = {
        "query": "hi hows life",
        "include_ml": False,
        "limit": 5,
    }
    response = client.post("/api/v1/copilot/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "general"
    assert "CrewAI Two-Agent Quality Layer" in data["activated_agents"]
    # Ensure heavy specialist workers were bypassed
    assert not any("SOP Agent" in a for a in data["activated_agents"])
    assert not any("Investigation Agent" in a for a in data["activated_agents"])
    assert data["sql_query"] == ""
    assert data["data_summary"]["row_count"] == 0
    assert len(data["final_report"]) > 50
    # Must NOT prepend the unrequested crisis heading
    assert "## Executive Intelligence Memorandum" not in data["final_report"]
