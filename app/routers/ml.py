"""
FastAPI Router for ML Predictive Forecasting and TreeSHAP Explainability.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import User, get_current_user
from app.agents.coordinator.schemas import IncidentInput, ImpactResult
from app.services.ml_service import MLService
from app.services.shap_service import SHAPService

router = APIRouter(prefix="/api/v1", tags=["Predictive ML & XAI"])

_ml_service: MLService | None = None
_shap_service: SHAPService | None = None


def get_ml_service() -> MLService:
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service


def get_shap_service() -> SHAPService:
    global _shap_service
    if _shap_service is None:
        _shap_service = SHAPService(get_ml_service())
    return _shap_service


@router.post(
    "/predict",
    response_model=ImpactResult,
    summary="Agent 2: ML Impact Forecasting & Resilience Triage (JWT Protected)",
)
def predict_impact(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    """Feeds incident into XGBoost models to compute downtime %, financial loss $, Resilience Score, and P1-P4 triage."""
    try:
        from app.agents.coordinator.impact_agent import ImpactAgent
        agent = ImpactAgent(ml_service=get_ml_service(), shap_service=get_shap_service())
        return agent.assess(incident)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Impact assessment failed: {str(e)}",
        )


@router.post(
    "/explain",
    summary="Agent 2 XAI: Native TreeSHAP Waterfall Risk Attribution (JWT Protected)",
)
def explain_risk_drivers(
    incident: IncidentInput,
    target: str = "revenue_loss_usd",
    current_user: User = Depends(get_current_user),
):
    """Returns local TreeSHAP feature attributions and waterfall data for UI charts."""
    try:
        shap = get_shap_service()
        incident_dict = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
            "supplier_tier": incident.supplier_tier,
            "supplier_region": incident.supplier_region,
            "supplier_size": incident.supplier_size,
            "has_backup_supplier": 1 if incident.has_backup_supplier else 0,
            "disruption_severity": incident.disruption_severity,
        }

        if target == "production_impact_pct":
            return shap.explain_impact(incident_dict)
        elif target == "full_recovery_days":
            return shap.explain_recovery(incident_dict)
        else:
            return shap.explain_loss(incident_dict, impact_pct=incident.production_impact_pct)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation failed: {str(e)}",
        )
