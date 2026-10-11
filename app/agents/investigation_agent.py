"""
Investigation Agent (Agent 1).
Responsible for:
  1. Intake parsing and ontology validation.
  2. Retrieving historical analog cohorts from MySQL `v_disruption_details`.
  3. Computing cohort baseline statistics.
  4. Generating structured evidence for downstream agents.
"""

from typing import Any
from decimal import Decimal
from sqlalchemy import text
from app.services.db_service import engine
from app.agents.schemas import IncidentInput, InvestigationResult


class InvestigationAgent:
    def __init__(self):
        pass

    def investigate(self, incident: IncidentInput, limit_analogs: int = 5) -> InvestigationResult:
        """
        Executes historical cohort retrieval and statistical summarization
        for the given incident profile.
        """
        incident_dict = incident.model_dump()

        # Build parameterized cohort query against MySQL unified view
        cohort_sql = text("""
            SELECT 
                COUNT(*) AS cohort_size,
                AVG(production_impact_pct) AS avg_impact_pct,
                AVG(revenue_loss_usd) AS avg_revenue_loss,
                AVG(full_recovery_days) AS avg_recovery_days,
                AVG(resilience_score) AS avg_resilience_score
            FROM v_disruption_details
            WHERE disruption_type = :disruption_type
              AND industry = :industry
              AND supplier_tier = :supplier_tier
              AND supplier_region = :supplier_region;
        """)

        analogs_sql = text("""
            SELECT 
                disruption_id,
                disruption_type,
                industry,
                supplier_tier,
                supplier_region,
                disruption_severity,
                production_impact_pct,
                revenue_loss_usd,
                response_type,
                full_recovery_days,
                resilience_score,
                prioritization_level,
                top_risk_driver
            FROM v_disruption_details
            WHERE disruption_type = :disruption_type
              AND industry = :industry
              AND supplier_tier = :supplier_tier
              AND supplier_region = :supplier_region
            ORDER BY ABS(CAST(disruption_severity AS SIGNED) - :severity) ASC, revenue_loss_usd DESC
            LIMIT :limit;
        """)

        params = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
            "supplier_tier": str(incident.supplier_tier),
            "supplier_region": incident.supplier_region,
            "severity": incident.disruption_severity,
            "limit": limit_analogs,
        }

        with engine.connect() as conn:
            # 1. Fetch cohort aggregate statistics
            cohort_stats = conn.execute(cohort_sql, params).mappings().fetchone()
            
            # 2. Fetch specific analog cases
            analog_rows = conn.execute(analogs_sql, params).mappings().fetchall()

        # Clean decimal / numerical types for JSON compatibility
        def clean_val(v: Any) -> Any:
            if isinstance(v, Decimal):
                return float(v)
            return v

        clean_analogs = [
            {k: clean_val(v) for k, v in dict(row).items()}
            for row in analog_rows
        ]

        cohort_size = int(cohort_stats["cohort_size"] or 0)
        avg_impact = round(float(cohort_stats["avg_impact_pct"] or 0.0), 2)
        avg_loss = round(float(cohort_stats["avg_revenue_loss"] or 0.0), 2)
        avg_rec = round(float(cohort_stats["avg_recovery_days"] or 0.0), 1)
        avg_res = round(float(cohort_stats["avg_resilience_score"] or 0.0), 2)

        # Synthesize investigative findings
        findings = (
            f"Retrieved {cohort_size:,} historical incident analogs for {incident.disruption_type} "
            f"affecting Tier {incident.supplier_tier} {incident.industry} suppliers in {incident.supplier_region}. "
            f"Cohort historical baseline: {avg_impact}% mean production downtime, "
            f"${avg_loss:,.2f} average revenue loss, and {avg_rec} days to full operational recovery "
            f"(Mean Resilience Score: {avg_res}%)."
        )

        return InvestigationResult(
            incident_profile=incident_dict,
            cohort_filter={
                "disruption_type": incident.disruption_type,
                "industry": incident.industry,
                "supplier_tier": incident.supplier_tier,
                "supplier_region": incident.supplier_region,
                "severity": incident.disruption_severity,
            },
            cohort_sample_size=cohort_size,
            analog_cases=clean_analogs,
            cohort_benchmarks={
                "avg_production_impact_pct": avg_impact,
                "avg_revenue_loss_usd": avg_loss,
                "avg_recovery_days": avg_rec,
                "avg_resilience_score": avg_res,
            },
            summary_findings=findings,
        )


if __name__ == "__main__":
    agent = InvestigationAgent()
    sample_incident = IncidentInput(
        disruption_type="Cyber Attack",
        industry="Electronics",
        supplier_tier=2,
        supplier_region="Asia-Pacific",
        supplier_size="Large",
        has_backup_supplier=False,
        disruption_severity=4,
    )
    result = agent.investigate(sample_incident)
    print("=== Investigation Agent Test ===")
    print("Cohort size:", result.cohort_sample_size)
    print("Findings:", result.summary_findings)
    print("First analog:", result.analog_cases[0] if result.analog_cases else "None")
