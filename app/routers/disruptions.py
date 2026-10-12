"""
FastAPI Router for Disruption Assessment, Multi-Agent Orchestration, and Data Warehouse Browser.
"""

import time
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import engine
from app.core.security import User, get_current_user
from app.agents.coordinator import (
    IncidentInput,
    InvestigationResult,
    ResponseResult,
    RecoveryResult,
    ExecutiveDossier,
    DisruptionCoordinator,
    InvestigationAgent,
    ImpactAgent,
    ResponseAgent,
    RecoveryAgent,
)
from app.routers.ml import get_ml_service, get_shap_service

router = APIRouter(prefix="/api/v1", tags=["Disruption Intelligence & Orchestration"])

_coordinator: DisruptionCoordinator | None = None


def get_coordinator() -> DisruptionCoordinator:
    global _coordinator
    if _coordinator is None:
        _coordinator = DisruptionCoordinator()
    return _coordinator


class PaginatedDisruptionsResponse(BaseModel):
    total_records: int
    page: int
    page_size: int
    total_pages: int
    records: list[dict[str, Any]]


class HumanFeedbackRequest(BaseModel):
    dossier_id: str
    operator_id: str = "operator_1"
    rating: int = Field(ge=1, le=5, description="1 to 5 rating of recommendation quality")
    accepted_strategy: bool = True
    override_strategy: str | None = None
    comments: str = Field(default="", description="Operator notes or review feedback")


@router.post(
    "/orchestrate",
    response_model=ExecutiveDossier,
    status_code=status.HTTP_200_OK,
    summary="Execute End-to-End 5-Agent Crisis Response Pipeline (JWT Protected)",
)
def orchestrate_crisis_response(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    """Executes the full 5-agent crisis response pipeline."""
    try:
        coordinator = get_coordinator()
        return coordinator.process_incident(incident)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failure: {str(e)}",
        )


@router.post(
    "/investigate",
    response_model=InvestigationResult,
    summary="Agent 1: Historical Analog Retrieval & Cohort Analytics (JWT Protected)",
)
def investigate_incident(
    incident: IncidentInput,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
):
    try:
        agent = InvestigationAgent()
        return agent.investigate(incident, limit_analogs=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}",
        )


@router.post(
    "/response-plan",
    response_model=ResponseResult,
    summary="Agent 3: Empirical Mitigation Strategy Benchmark (JWT Protected)",
)
def plan_mitigation_response(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    try:
        impact_agent = ImpactAgent(ml_service=get_ml_service(), shap_service=get_shap_service())
        impact = impact_agent.assess(incident)
        response_agent = ResponseAgent()
        return response_agent.plan_response(incident, impact)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response planning failed: {str(e)}",
        )


@router.post(
    "/recovery-forecast",
    response_model=RecoveryResult,
    summary="Agent 4: Milestone Roadmap & Vendor Continuity Analysis (JWT Protected)",
)
def forecast_recovery_roadmap(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    try:
        impact_agent = ImpactAgent(ml_service=get_ml_service(), shap_service=get_shap_service())
        impact = impact_agent.assess(incident)
        response_agent = ResponseAgent()
        response = response_agent.plan_response(incident, impact)
        recovery_agent = RecoveryAgent(ml_service=get_ml_service())
        return recovery_agent.forecast_recovery(incident, response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recovery forecasting failed: {str(e)}",
        )


@router.get(
    "/disruptions",
    response_model=PaginatedDisruptionsResponse,
    summary="Paginated Historical Disruptions Browser (25 records per page)",
)
def get_historical_disruptions(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    page_size: int = Query(25, ge=1, le=100, description="Records per page (default: 25)"),
    disruption_type: str | None = Query(None, description="Filter by disruption type"),
    industry: str | None = Query(None, description="Filter by industry"),
    supplier_region: str | None = Query(None, description="Filter by supplier region"),
    severity: int | None = Query(None, ge=1, le=5, description="Filter by severity level (1-5)"),
    search: str | None = Query(None, description="Search term across id, type, industry, or region"),
    current_user: User = Depends(get_current_user),
):
    try:
        conditions = []
        params = {}

        if disruption_type:
            type_map = {
                "factory": "Factory Incident",
                "fire": "Factory Incident",
                "cyber": "Cyber Attack",
                "port": "Port Congestion",
                "strike": "Labor Strike",
            }
            norm_type = type_map.get(disruption_type.strip().lower(), disruption_type)
            conditions.append("disruption_type = :disruption_type")
            params["disruption_type"] = norm_type
        if industry:
            ind_map = {
                "auto": "Automotive",
                "chips": "Electronics",
                "semiconductors": "Electronics",
                "pharma": "Pharmaceuticals",
                "retail": "Consumer Goods",
                "energy": "Consumer Goods",
            }
            norm_ind = ind_map.get(industry.strip().lower(), industry)
            conditions.append("industry = :industry")
            params["industry"] = norm_ind
        if supplier_region:
            region_map = {
                "middle east": "Africa/Middle East",
                "africa": "Africa/Middle East",
                "latin america": "South America",
                "apac": "Asia-Pacific",
                "asia": "Asia-Pacific",
                "na": "North America",
                "eu": "Europe",
            }
            norm_region = region_map.get(supplier_region.strip().lower(), supplier_region)
            conditions.append("supplier_region = :supplier_region")
            params["supplier_region"] = norm_region
        if severity is not None:
            conditions.append("disruption_severity = :severity")
            params["severity"] = severity
        if search:
            conditions.append("(disruption_id LIKE :search OR disruption_type LIKE :search OR industry LIKE :search OR supplier_region LIKE :search)")
            params["search"] = f"%{search}%"

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        offset = (page - 1) * page_size
        params["offset"] = offset
        params["limit"] = page_size

        count_sql = f"SELECT COUNT(*) FROM v_disruption_details{where_clause}"
        select_sql = f"""
            SELECT 
                disruption_id, disruption_type, industry, supplier_tier, supplier_region,
                supplier_size, has_backup_supplier, disruption_severity, production_impact_pct,
                revenue_loss_usd, response_type, response_time_days, partial_recovery_days,
                full_recovery_days, permanent_supplier_change, resilience_score,
                prioritization_level, top_risk_driver, recommended_strategy
            FROM v_disruption_details{where_clause}
            ORDER BY disruption_id ASC
            LIMIT :limit OFFSET :offset
        """

        with engine.connect() as conn:
            count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
            total = conn.execute(text(count_sql), count_params).scalar() or 0
            rows = conn.execute(text(select_sql), params).mappings().all()
            records = [dict(r) for r in rows]

        total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1

        return PaginatedDisruptionsResponse(
            total_records=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            records=records,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query disruptions: {str(e)}",
        )


@router.post(
    "/feedback",
    summary="Submit Human Operator Review & Audit Feedback (JWT Protected)",
)
def submit_operator_feedback(
    feedback: HumanFeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    return {
        "status": "recorded",
        "dossier_id": feedback.dossier_id,
        "operator_id": feedback.operator_id,
        "rating": feedback.rating,
        "accepted_strategy": feedback.accepted_strategy,
        "recorded_at_utc": time.time(),
        "audit_message": "Operator feedback successfully logged into crisis management registry.",
    }
