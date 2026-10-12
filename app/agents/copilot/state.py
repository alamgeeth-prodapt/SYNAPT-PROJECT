"""
LangGraph Supervisor state definition for Executive AI Copilot.
Modeled directly after D:\\Project_2\\langgraph_state.py.
"""

from typing import Any, TypedDict


class CopilotSupervisorState(TypedDict, total=False):
    user_query: str
    include_ml: bool
    limit: int
    intent: str
    next: str
    agent_context: dict[str, Any]
    execution_trace: list[dict[str, Any]]
    final_response: str
    raw_draft: str
    review_trace: dict[str, Any]
    engine_used: str
    activated_agents: list[str]
    sop_data: dict[str, Any] | None
    sql_result: dict[str, Any] | None
    ml_metrics: dict[str, Any] | None
