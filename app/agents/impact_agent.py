"""
Impact Assessment Agent (Agent 2).
Responsible for:
  1. Multi-target machine learning inference via MLService (XGBoost).
  2. Quantitative impact forecasting (downtime %, financial loss $, recovery days).
  3. Dynamic composite Resilience Score & P1-P4 Triage Prioritization.
  4. Local TreeSHAP attribution and root-cause risk driver extraction via SHAPService.
"""

from typing import Any
from app.services.ml_service import MLService
from app.services.shap_service import SHAPService
from app.agents.schemas import IncidentInput, ImpactResult


class ImpactAgent:
    def __init__(self, ml_service: MLService | None = None, shap_service: SHAPService | None = None):
        self.ml_service = ml_service or MLService()
        self.shap_service = shap_service or SHAPService(self.ml_service)

    def assess(self, incident: IncidentInput) -> ImpactResult:
        """
        Executes end-to-end impact evaluation, resilience scoring, and
        TreeSHAP risk driver attribution for the incident.
        """
        incident_dict = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
            "supplier_tier": incident.supplier_tier,
            "supplier_region": incident.supplier_region,
            "supplier_size": incident.supplier_size,
            "has_backup_supplier": 1 if incident.has_backup_supplier else 0,
            "disruption_severity": incident.disruption_severity,
        }

        # 1. Run ML assessment (predictions + resilience score + triage level)
        ml_eval = self.ml_service.assess_incident(incident_dict)

        # 2. Run SHAP attribution for financial loss and downtime
        loss_explanation = self.shap_service.explain_loss(
            incident_dict, impact_pct=ml_eval["predicted_impact_pct"]
        )
        shap_narrative = self.shap_service.get_risk_driver_narrative(loss_explanation)

        return ImpactResult(
            predicted_production_impact_pct=ml_eval["predicted_impact_pct"],
            predicted_revenue_loss_usd=ml_eval["predicted_revenue_loss_usd"],
            predicted_recovery_days=ml_eval["predicted_full_recovery_days"],
            resilience_score=ml_eval["resilience_score"],
            prioritization_level=ml_eval["prioritization_level"],
            top_risk_drivers=loss_explanation["top_risk_drivers"],
            shap_narrative=shap_narrative,
            feature_attributions=loss_explanation["features"],
        )


if __name__ == "__main__":
    agent = ImpactAgent()
    sample = IncidentInput(
        disruption_type="Cyber Attack",
        industry="Electronics",
        supplier_tier=2,
        supplier_region="Asia-Pacific",
        supplier_size="Large",
        has_backup_supplier=False,
        disruption_severity=4,
    )
    result = agent.assess(sample)
    print("=== Impact Agent Test ===")
    print("Triage:", result.prioritization_level)
    print("Downtime:", result.predicted_production_impact_pct, "%")
    print("Loss:", f"${result.predicted_revenue_loss_usd:,.2f}")
    print("Resilience Score:", result.resilience_score, "%")
    print("SHAP Narrative:", result.shap_narrative)
