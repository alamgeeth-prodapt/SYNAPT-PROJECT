"""
Executive AI Copilot Multi-Agent Package.
Architecture:
- LangGraph Supervisor StateGraph (Supervisor -> Specialist Workers -> Customer Comms Crew -> END)
- Synapt Trident Embedding Storage Provider (supply_chain_sop)
- CrewAI Two-Agent Customer Communications Crew powered by Google Gemini (gemini-3.5-flash-lite)
"""

from app.agents.copilot.schemas import (
    CopilotChatRequest,
    CopilotChatResponse,
    AgentTrace,
    AgentDrafterTrace,
    AgentReviewerTrace,
)
from app.agents.copilot.state import CopilotSupervisorState
from app.agents.copilot.graph import copilot_graph, build_copilot_graph
from app.agents.copilot.orchestrator import TwoAgentCopilotOrchestrator

__all__ = [
    "CopilotChatRequest",
    "CopilotChatResponse",
    "AgentTrace",
    "AgentDrafterTrace",
    "AgentReviewerTrace",
    "CopilotSupervisorState",
    "copilot_graph",
    "build_copilot_graph",
    "TwoAgentCopilotOrchestrator",
]
