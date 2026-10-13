"""
FastAPI Microservice for AI-Powered Supply Chain Disruption Assistant with Synapt.
Serves the Multi-Agent Orchestration Engine, Executive AI Copilot, Predictive ML Models,
TreeSHAP, Synapt Trident MCP Knowledge Graph, and Graph-Guided SQL Builder.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    health_router,
    auth_router,
    copilot_router,
    disruptions_router,
    query_router,
    ml_router,
    analytics_router,
)

# ==============================================================================
# FastAPI App Initialization & Metadata
# ==============================================================================

app = FastAPI(
    title="Synapt Supply Chain Disruption Assistant API",
    description="""
### AI-Powered Multi-Agent Supply Chain Resilience & Disruption Assistant

This REST API serves the end-to-end resilience engine:
* **Executive AI Copilot**: LangGraph Supervisor + CrewAI 2-agent customer comms grounded in Synapt Trident.
* **Multi-Agent Orchestration**: Investigation, Impact, Response, Recovery, and LLM-as-Judge agents.
* **Predictive ML & XAI**: XGBoost regression models for downtime, revenue loss, and recovery with native TreeSHAP attribution.
* **Synapt Trident MCP**: Semantic knowledge graph ontology governance and just-in-time value grounding.
* **Safe SQL Engine**: Graph-guided read-only SQL generation querying 100,000 historical disruption records (`v_disruption_details`).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend applications (React on Vite / Create React App / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Router Assembly
# ==============================================================================

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(copilot_router)
app.include_router(disruptions_router)
app.include_router(query_router)
app.include_router(ml_router)
app.include_router(analytics_router)

# Pre-warm analytics cache in background thread on startup
import threading
def _warmup_analytics_cache():
    try:
        from app.routers.analytics import get_analytics_overview
        from app.core.security import User
        get_analytics_overview(current_user=User(username="system_warmup", role="admin"))
    except Exception as e:
        pass

threading.Thread(target=_warmup_analytics_cache, daemon=True).start()

