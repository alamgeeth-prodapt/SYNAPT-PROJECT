"""
LangGraph Supervisor Node for Executive AI Copilot.
Modeled directly after D:\\Project_2\\supervisor.py.
"""

from app.agents.copilot.state import CopilotSupervisorState


async def supervisor(state: CopilotSupervisorState) -> CopilotSupervisorState:
    """
    Supervisor router node:
    1. Analyzes query keywords to determine query intent (SOP vs. SQL Analytics vs. Predictive vs. Crisis).
    2. Builds an execution plan list of workers if not yet planned.
    3. Guarantees that 'customer_comms_crew' is ALWAYS the terminal worker.
    4. Routes to the next uncompleted worker node, or transitions to 'finish' once all complete.
    """
    query = state.get("user_query", "").strip()
    context = state.get("agent_context", {}).copy()

    if "_plan" not in context:
        plan = []
        q_lower = query.lower()
        is_sop = any(w in q_lower for w in ["sop", "procedure", "checklist", "playbook", "containment", "sla", "protocol"])
        is_sql = any(w in q_lower for w in ["historical", "past", "history", "records", "database", "average", "avg", "count", "cases", "sql", "cohort", "v_disruption_details"])
        is_predictive = any(w in q_lower for w in ["predict", "forecast", "projection", "expected loss", "estimate loss", "future loss"])

        # Domain keywords indicating an actual supply chain crisis scenario
        crisis_keywords = [
            "disruption", "disruptions", "crisis", "incident", "incidents", "outage", "downtime",
            "cyber", "attack", "hack", "ransomware",
            "port", "congestion", "shipping", "freight", "logistics", "maritime",
            "strike", "labor", "walkout", "union",
            "geopolitical", "tariff", "sanctions", "war", "embargo",
            "natural disaster", "disaster", "earthquake", "flood", "typhoon", "tsunami", "hurricane", "storm",
            "factory", "plant", "fire", "explosion",
            "supplier", "suppliers", "vendor", "vendors", "supply chain",
            "tier 1", "tier-1", "tier 2", "tier-2", "tier 3", "tier-3", "tier 4", "tier-4",
            "mitigation", "reroute", "backup supplier", "dual source", "dual-source",
            "revenue loss", "production impact", "recovery days", "resilience",
            "aerospace", "automotive", "electronics", "pharmaceuticals", "consumer goods",
            "asia-pacific", "apac", "europe", "north america", "latin america", "middle east",
        ]
        is_crisis = any(w in q_lower for w in crisis_keywords)

        if is_sop and not is_sql:
            intent = "sop"
            plan.append("sop_retriever")
        elif is_sql and not is_sop and not is_predictive:
            intent = "sql_analytics"
            plan.append("investigation_worker")
            if state.get("include_ml", True):
                plan.append("impact_worker")
        elif is_predictive and not is_sop and not is_sql:
            intent = "predictive"
            plan.append("investigation_worker")
            if state.get("include_ml", True):
                plan.append("impact_worker")
        elif is_crisis:
            intent = "crisis"
            plan.append("sop_retriever")
            plan.append("investigation_worker")
            if state.get("include_ml", True):
                plan.append("impact_worker")
        else:
            # If nothing classifies (e.g. conversational greetings, general inquiries), go directly to CrewAI
            intent = "general"

        # Always finish with customer comms crew (matching D:\Project_2 supervisor pattern)
        plan.append("customer_comms_crew")
        context["_plan"] = plan
        context["_completed_workers"] = []
        context["_intent"] = intent

    plan = context["_plan"]
    completed = context["_completed_workers"]
    intent = context.get("_intent", "crisis")

    for worker in plan:
        if worker not in completed:
            return {
                **state,
                "intent": intent,
                "agent_context": context,
                "next": worker,
            }

    return {
        **state,
        "intent": intent,
        "agent_context": context,
        "next": "finish",
    }
