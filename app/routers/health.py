"""
FastAPI Router for System Health, Readiness, and Diagnostics.
"""

import time
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.core.database import engine
from app.routers.ml import get_ml_service

router = APIRouter(tags=["System Health & Diagnostics"])


class HealthResponse(BaseModel):
    status: str
    database: str
    total_records: int
    models_loaded: list[str]
    synapt_mcp: str
    timestamp_utc: float


@router.get("/")
def root():
    return {
        "message": "Synapt Supply Chain Disruption Assistant API is online.",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Verifies MySQL connection, loaded models, and Synapt service readiness."""
    try:
        with engine.connect() as conn:
            row_count = conn.execute(text("SELECT COUNT(*) FROM v_disruption_details")).scalar()
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        row_count = 0

    ml = get_ml_service()
    loaded_models = list(ml.metrics.keys())

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        total_records=row_count or 0,
        models_loaded=loaded_models,
        synapt_mcp="configured",
        timestamp_utc=time.time(),
    )
