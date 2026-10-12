"""
Investigation Worker (Synapt Schema Ontology + Gemini SQL Builder).
Executes safe read-only SQL on MySQL v_disruption_details using ontology grounding.
"""

from app.agents.copilot.state import CopilotSupervisorState
from app.services.sql_builder import build_and_execute_sql_async


async def investigation_worker(state: CopilotSupervisorState) -> CopilotSupervisorState:
    query = state.get("user_query", "")
    limit = state.get("limit", 15)

    try:
        sql_result = await build_and_execute_sql_async(query, limit=limit, use_synapt=True)
    except Exception as e:
        sql_result = {
            "generated_sql": "SELECT * FROM v_disruption_details LIMIT 15;",
            "records": [],
            "columns": [],
            "injected_classes": {},
            "execution_time_ms": 0.0,
            "error": str(e),
        }

    context = state.get("agent_context", {}).copy()
    context["investigation_worker"] = sql_result

    completed = context.get("_completed_workers", []).copy()
    if "investigation_worker" not in completed:
        completed.append("investigation_worker")
    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "Investigation Agent (Synapt Schema + Gemini SQL)",
        "output": f"Generated SQL executed: {len(sql_result.get('records', []))} rows",
    })

    activated = state.get("activated_agents", []).copy()
    agent_label = "Investigation Agent (Synapt Schema + Gemini SQL)"
    if agent_label not in activated:
        activated.append(agent_label)

    return {
        **state,
        "agent_context": context,
        "execution_trace": trace,
        "activated_agents": activated,
        "sql_result": sql_result,
        "next": "supervisor",
    }
