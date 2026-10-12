"""
LangGraph StateGraph compiler for Executive AI Copilot.
Modeled directly after D:\\Project_2\\graph.py.
"""

from langgraph.graph import StateGraph, START, END

from app.agents.copilot.state import CopilotSupervisorState
from app.agents.copilot.supervisor import supervisor
from app.agents.copilot.workers.sop_worker import sop_worker
from app.agents.copilot.workers.investigation_worker import investigation_worker
from app.agents.copilot.workers.impact_worker import impact_worker
from app.agents.copilot.workers.customer_comms_crew import customer_comms_worker


def build_copilot_graph():
    """
    Constructs and compiles the StateGraph multi-agent orchestration pipeline:
    START -> supervisor -> [specialists] -> supervisor -> customer_comms_crew -> END
    """
    graph = StateGraph(CopilotSupervisorState)

    # Nodes
    graph.add_node("supervisor", supervisor)
    graph.add_node("sop_retriever", sop_worker)
    graph.add_node("investigation_worker", investigation_worker)
    graph.add_node("impact_worker", impact_worker)
    graph.add_node("customer_comms_crew", customer_comms_worker)

    # Entry edge
    graph.add_edge(START, "supervisor")

    # Supervisor router
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "sop_retriever": "sop_retriever",
            "investigation_worker": "investigation_worker",
            "impact_worker": "impact_worker",
            "customer_comms_crew": "customer_comms_crew",
            "finish": END,
        },
    )

    # Specialist workers return to supervisor
    graph.add_edge("sop_retriever", "supervisor")
    graph.add_edge("investigation_worker", "supervisor")
    graph.add_edge("impact_worker", "supervisor")

    # Final response generation edges to END
    graph.add_edge("customer_comms_crew", END)

    return graph.compile()


copilot_graph = build_copilot_graph()
