"""
FastAPI Routers Package.
Exports modular routers for Auth, Copilot, Disruptions, Query, ML, and Health.
"""

from app.routers.auth import router as auth_router
from app.routers.copilot import router as copilot_router
from app.routers.disruptions import router as disruptions_router
from app.routers.query import router as query_router
from app.routers.ml import router as ml_router
from app.routers.health import router as health_router

__all__ = [
    "auth_router",
    "copilot_router",
    "disruptions_router",
    "query_router",
    "ml_router",
    "health_router",
]
