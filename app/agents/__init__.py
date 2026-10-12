"""
Multi-Agent Orchestration Package.
Exports both:
1. Traditional Disruption Coordinator Pipeline (app.agents.coordinator)
2. LangGraph Supervisor + CrewAI Executive Copilot (app.agents.copilot)
"""

from app.agents.coordinator import (
    IncidentInput,
    InvestigationResult,
    ImpactResult,
    ResponseResult,
    RecoveryResult,
    ExecutiveDossier,
    Milestone,
    StrategyComparison,
    JudgeVerdict,
    InvestigationAgent,
    ImpactAgent,
    ResponseAgent,
    RecoveryAgent,
    LLMJudgeAgent,
    DisruptionCoordinator,
)
from app.agents.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    AgentTrace,
    AgentDrafterTrace,
    AgentReviewerTrace,
    CopilotSupervisorState,
    TwoAgentCopilotOrchestrator,
    copilot_graph,
    build_copilot_graph,
)

__all__ = [
    # Coordinator
    "IncidentInput",
    "InvestigationResult",
    "ImpactResult",
    "ResponseResult",
    "RecoveryResult",
    "ExecutiveDossier",
    "Milestone",
    "StrategyComparison",
    "JudgeVerdict",
    "InvestigationAgent",
    "ImpactAgent",
    "ResponseAgent",
    "RecoveryAgent",
    "LLMJudgeAgent",
    "DisruptionCoordinator",
    # Copilot
    "CopilotChatRequest",
    "CopilotChatResponse",
    "AgentTrace",
    "AgentDrafterTrace",
    "AgentReviewerTrace",
    "CopilotSupervisorState",
    "TwoAgentCopilotOrchestrator",
    "copilot_graph",
    "build_copilot_graph",
]
