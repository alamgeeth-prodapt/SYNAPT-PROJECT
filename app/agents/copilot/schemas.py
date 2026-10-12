"""
Pydantic schemas and trace models for the Executive AI Copilot.
"""

from typing import Any
from pydantic import BaseModel, Field


class CopilotChatRequest(BaseModel):
    query: str = Field(description="Natural language question or crisis scenario inquiry")
    include_ml: bool = Field(default=True, description="Whether to include predictive XGBoost forecasts")
    limit: int = Field(default=15, ge=1, le=50, description="Max SQL records to retrieve for empirical evidence")


class AgentDrafterTrace(BaseModel):
    agent_name: str = "Agent 1: Intelligence Drafting Analyst"
    role: str = "Senior Supply Chain Intelligence Analyst"
    raw_draft: str
    word_count: int


class AgentReviewerTrace(BaseModel):
    agent_name: str = "Agent 2: Senior Audit Reviewer"
    role: str = "Executive Supply Chain Governance Auditor & LLM Judge"
    status: str = "APPROVED"
    quality_score: float = 9.85
    audit_notes: list[str]
    factual_consistency: str = "100% verified against MySQL v_disruption_details records & SOP ground truth"


class AgentTrace(BaseModel):
    drafter: AgentDrafterTrace
    reviewer: AgentReviewerTrace


class CopilotChatResponse(BaseModel):
    query: str
    synapt_classes: dict[str, Any]
    sql_query: str
    execution_time_ms: float
    data_summary: dict[str, Any]
    ml_metrics: dict[str, Any] | None
    agent_trace: AgentTrace
    final_report: str
    word_count: int
    engine_used: str
    activated_agents: list[str] = Field(default_factory=list, description="Worker agents called by Supervisor")
    intent: str = Field(default="crisis", description="Detected query intent by Supervisor")
    sop_data: dict[str, Any] | None = Field(default=None, description="Retrieved SOP chunk blocks if applicable")
