"""
FastAPI Router for Executive AI Copilot & Two-Agent Report Generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import User, get_current_user
from app.agents.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    TwoAgentCopilotOrchestrator,
)

router = APIRouter(prefix="/api/v1/copilot", tags=["Executive AI Copilot"])

orchestrator = TwoAgentCopilotOrchestrator()


@router.post(
    "/chat",
    response_model=CopilotChatResponse,
    summary="Query Copilot with Natural Language (Synapt Schema -> Safe SQL -> 2-Agent Report)",
)
async def copilot_chat(
    req: CopilotChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Executes the 5-stage Executive AI Copilot intelligence pipeline:
    1. Synapt Trident MCP Schema & Ontology Retrieval
    2. Grounded Read-Only SQL Synthesis & Execution on MySQL v_disruption_details
    3. Predictive XGBoost Model Inference (Downtime %, Revenue Loss, Recovery Days)
    4. Agent 1 (Intelligence Drafting Analyst): Drafts comprehensive 400-500 word report
    5. Agent 2 (Senior Audit Reviewer / LLM Judge): Audits and fact-checks against empirical data
    """
    try:
        res = await orchestrator.execute_copilot_workflow(req)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Executive Copilot pipeline error: {str(e)}",
        )


@router.get(
    "/status",
    summary="Check Executive Copilot Capabilities & Engine Status",
)
async def copilot_status(
    current_user: User = Depends(get_current_user),
):
    """Returns whether live LLM (Google Gemini / Anthropic / OpenAI) or offline empirical engine is active."""
    provider = (
        "google_gemini"
        if orchestrator.gemini_api_key
        else "anthropic_claude"
        if orchestrator.anthropic_api_key
        else "openai_gpt"
        if orchestrator.openai_api_key
        else "empirical_engine"
    )
    return {
        "engine": provider if orchestrator.has_live_llm else "empirical_engine",
        "live_llm_available": orchestrator.has_live_llm,
        "provider": provider,
        "framework": "LangGraph Supervisor + Google ADK + CrewAI",
        "primary_llm": "Google Gemini (gemini-3.5-flash-lite)"
        if orchestrator.gemini_api_key
        else "Anthropic Claude (claude-3-5-sonnet)"
        if orchestrator.anthropic_api_key
        else "OpenAI GPT"
        if orchestrator.openai_api_key
        else "Deterministic Empirical Synthesis Engine",
        "models": {
            "supervisor": "gemini-3.5-flash-lite",
            "drafter": "gemini-3.5-flash-lite",
            "reviewer": "gemini-3.5-flash-lite",
            "sql": "gemini-3.5-flash-lite",
        },
        "agents": [
            {
                "name": "Supervisor: LangGraph Router",
                "role": "Intent Classifier & Agent Orchestrator",
                "task": "Dispatches queries to SOP, SQL, or ML agents based on query intent",
            },
            {
                "name": "Worker 1: SOP Retrieval Agent",
                "role": "Synapt SOP Provider Agent",
                "task": "Retrieves 6 structured SOP playbook chunks from supply_chain_sop",
            },
            {
                "name": "Worker 2: Investigation Agent",
                "role": "Gemini SQL Synthesizer & Warehouse Querier",
                "task": "Synthesizes read-only SQL on MySQL v_disruption_details using Synapt ontology",
            },
            {
                "name": "Worker 3: Impact Agent",
                "role": "XGBoost Predictive Modeler",
                "task": "Computes predictive ML forecasts for downtime %, revenue loss, and recovery days",
            },
            {
                "name": "Agent 1: Intelligence Drafting Analyst",
                "role": "Senior Supply Chain Intelligence Analyst",
                "task": "Synthesizes empirical data and writes 400-500 word executive draft or 6-chunk SOP",
            },
            {
                "name": "Agent 2: Senior Audit Reviewer",
                "role": "Executive Supply Chain Governance Auditor & LLM Judge",
                "task": "Fact-checks draft against MySQL records and Synapt ontology",
            },
        ],
        "reporting_standard": "400-500 Word Executive Intelligence Memorandum / 6-Chunk SOP",
    }
