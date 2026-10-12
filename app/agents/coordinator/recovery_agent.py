"""
Recovery Analysis Agent (Agent 4).
Responsible for:
  1. Forecasting target milestone operational recovery schedules.
  2. Evaluating permanent supplier substitution risk from historical data.
  3. Generating a 4-stage recovery milestone roadmap.
  4. Establishing post-recovery audit and KPI verification checklists.
"""

from typing import Any
from sqlalchemy import text
from app.core.database import engine
from app.services.ml_service import MLService
from app.agents.coordinator.schemas import IncidentInput, ResponseResult, RecoveryResult, Milestone


class RecoveryAgent:
    def __init__(self, ml_service: MLService | None = None):
        self.ml_service = ml_service or MLService()

    def forecast_recovery(
        self, incident: IncidentInput, response: ResponseResult
    ) -> RecoveryResult:
        """
        Calculates recovery timeline under the recommended strategy, assesses
        supplier continuity risk, and constructs the milestone schedule.
        """
        # 1. Simulate recovery days under the recommended strategy
        incident_dict = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
            "supplier_tier": incident.supplier_tier,
            "supplier_region": incident.supplier_region,
            "supplier_size": incident.supplier_size,
            "has_backup_supplier": 1 if incident.has_backup_supplier else 0,
            "disruption_severity": incident.disruption_severity,
        }

        scenario = {
            "response_type": response.recommended_strategy,
            "response_time_days": response.response_sla_days,
            "partial_recovery_days": max(3, response.response_sla_days + 4),
            "permanent_supplier_change": 0,
        }

        forecasted_days = round(
            self.ml_service.predict_recovery_days(incident_dict, scenario_overrides=scenario),
            1,
        )

        # 2. Query historical permanent supplier change probability from MySQL
        rate_sql = text("""
            SELECT 
                COUNT(*) AS total_cases,
                SUM(permanent_supplier_change) AS perm_changes
            FROM v_disruption_details
            WHERE disruption_type = :disruption_type
              AND industry = :industry
              AND supplier_tier = :supplier_tier;
        """)

        params = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
            "supplier_tier": str(incident.supplier_tier),
        }

        with engine.connect() as conn:
            row = conn.execute(rate_sql, params).mappings().fetchone()
            total_cases = int(row["total_cases"] or 0)
            perm_changes = int(row["perm_changes"] or 0)

        if total_cases > 0:
            change_risk_pct = round((perm_changes / total_cases) * 100.0, 1)
        else:
            change_risk_pct = 25.0

        if change_risk_pct >= 40.0:
            continuity_rating = "High Risk"
        elif change_risk_pct >= 20.0:
            continuity_rating = "Moderate Risk"
        else:
            continuity_rating = "Stable"

        # 3. Construct 4-stage milestone schedule
        sla_day = response.response_sla_days
        partial_day = max(sla_day + 5, int(forecasted_days * 0.4))
        full_day = max(partial_day + 10, int(forecasted_days))

        milestones = [
            Milestone(
                stage="Phase 1: Incident Containment",
                target_day=0,
                description=f"Incident triaged and emergency mitigation plan approved for {incident.disruption_type}.",
            ),
            Milestone(
                stage=f"Phase 2: '{response.recommended_strategy}' Deployed",
                target_day=sla_day,
                description=f"Full operational execution of '{response.recommended_strategy}' within SLA threshold.",
            ),
            Milestone(
                stage="Phase 3: Partial Restoration (50% Throughput)",
                target_day=partial_day,
                description="Initial inventory buffer or secondary supplier batch delivered; production lines resume at 50% capacity.",
            ),
            Milestone(
                stage="Phase 4: Full Operational Normalcy (100% Throughput)",
                target_day=full_day,
                description="Full throughput restored, backlog cleared, and normal lead-times re-established.",
            ),
        ]

        # 4. Post-recovery audit checklist
        audit_checklist = [
            "Conduct root-cause post-mortem with affected supplier within 14 days of full recovery.",
            f"Review vendor continuity status (current contract attrition risk assessed at {change_risk_pct}%).",
            "Recalibrate minimum safety-stock thresholds in ERP based on actual outage duration.",
            "Verify complete reconciliation of scrap, expedited freight costs, and insurance loss claims.",
            "Execute vendor performance scorecard review and update second-source backup supplier contracts.",
        ]

        return RecoveryResult(
            forecasted_full_recovery_days=float(full_day),
            permanent_supplier_change_risk_pct=change_risk_pct,
            vendor_continuity_rating=continuity_rating,
            milestones=milestones,
            post_recovery_audit_checklist=audit_checklist,
        )


if __name__ == "__main__":
    from app.agents.impact_agent import ImpactAgent
    from app.agents.response_agent import ResponseAgent

    sample = IncidentInput(
        disruption_type="Cyber Attack",
        industry="Electronics",
        supplier_tier=2,
        supplier_region="Asia-Pacific",
        supplier_size="Large",
        has_backup_supplier=False,
        disruption_severity=4,
    )
    impact_res = ImpactAgent().assess(sample)
    response_res = ResponseAgent().plan_response(sample, impact_res)
    recovery_agent = RecoveryAgent()
    rec_res = recovery_agent.forecast_recovery(sample, response_res)

    print("=== Recovery Analysis Agent Test ===")
    print("Forecasted Days:", rec_res.forecasted_full_recovery_days)
    print("Continuity Risk:", rec_res.vendor_continuity_rating, f"({rec_res.permanent_supplier_change_risk_pct}%)")
    print("Milestones count:", len(rec_res.milestones))
    for m in rec_res.milestones:
        print(f"  Day {m.target_day}: {m.stage}")
