"""
SOP Retriever Worker (Synapt Trident Embedding Storage).
Retrieves raw document chunks and live grounded answers directly from Synapt without local file fallback.
"""

from app.agents.copilot.state import CopilotSupervisorState
from app.services.synapt_service import SynaptService


async def sop_worker(state: CopilotSupervisorState) -> CopilotSupervisorState:
    query = state.get("user_query", "")
    synapt = SynaptService()
    try:
        sop_data = await synapt.retrieve_sop_chunks(query, top_k=6)
    except Exception as e:
        sop_data = {"error": f"SOP retrieval bypassed: {str(e)}", "document_chunks": []}

    context = state.get("agent_context", {}).copy()
    context["sop_retriever"] = sop_data

    completed = context.get("_completed_workers", []).copy()
    if "sop_retriever" not in completed:
        completed.append("sop_retriever")
    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "SOP Agent (supply_chain_sop)",
        "output": f"Retrieved {len(sop_data.get('document_chunks', []))} embedding chunks from Synapt",
    })

    activated = state.get("activated_agents", []).copy()
    if "SOP Agent (supply_chain_sop)" not in activated:
        activated.append("SOP Agent (supply_chain_sop)")

    return {
        **state,
        "agent_context": context,
        "execution_trace": trace,
        "activated_agents": activated,
        "sop_data": sop_data,
        "next": "supervisor",
    }
