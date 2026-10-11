"""
Response Planning Agent (Agent 3).
Responsible for:
  1. Executing empirical strategy benchmarks on MySQL `v_disruption_details`.
  2. Comparing historical efficacy across response strategies (Alternative Supplier vs Production Reroute vs Inventory Buffer).
  3. Formulating primary and contingency mitigation playbooks.
  4. Establishing operational SLAs and actionable crisis checklists.
"""

from decimal import Decimal
from typing import Any
from sqlalchemy import text
from app.services.db_service import engine
from app.agents.schemas import IncidentInput, ImpactResult, ResponseResult, StrategyComparison


STRATEGY_CHECKLISTS: dict[str, list[str]] = {
    "Alternative Supplier": [
        "Activate secondary pre-qualified supplier agreements and trigger emergency allocation quotas.",
        "Authorize expedited freight (air/express) for initial critical batch replenishment.",
        "Validate supplier quality certification and component compatibility for swapped SKUs.",
        "Update ERP purchase orders with revised lead times and supplier master records.",
    ],
    "Production Reroute": [
        "Reassign work orders to secondary fabrication plant or alternate assembly line.",
        "Adjust manufacturing line tooling and verify component tooling parity.",
        "Coordinate inventory transfer of existing sub-assemblies to the destination plant.",
        "Notify logistics dispatch to redirect raw inbound freight to alternate receiving dock.",
    ],
    "Inventory Buffer": [
        "Audit current on-hand safety stock and work-in-progress (WIP) reserves across regional distribution centers.",
        "Institute priority allocation rationing for critical tier-1 customer contracts.",
        "Freeze non-essential inventory outbound shipments to preserve operational run-rate.",
        "Calculate stock depletion burn-rate vs estimated supplier recovery timeline.",
    ],
    "Combined Strategy": [
        "Implement hybrid multi-channel response: immediate buffer draw-down while initiating secondary supplier qualification.",
        "Reroute 40% of critical assembly volume to secondary regional facility.",
        "Trigger contingency vendor emergency contract and place spot market buffer orders.",
        "Establish daily executive war-room to monitor dual-track recovery milestones.",
    ],
    "Customer Delay": [
        "Identify customer contracts with force majeure or flexible SLA delay clauses.",
        "Issue formal delivery adjustment notifications with proactive revised ETA windows.",
        "Negotiate partial delivery schedules to fulfill high-priority customer commitments.",
        "Offer service credit waivers or freight subsidies to mitigate customer churn risk.",
    ],
}


class ResponseAgent:
    def __init__(self):
        pass

    def plan_response(self, incident: IncidentInput, impact: ImpactResult) -> ResponseResult:
        """
        Queries historical benchmarks on v_disruption_details and generates
        the empirical mitigation response plan.
        """
        # Benchmark query on exact cohort
        benchmark_sql = text("""
            SELECT 
                response_type,
                COUNT(*) AS incident_count,
                AVG(revenue_loss_usd) AS avg_revenue_loss,
                AVG(full_recovery_days) AS avg_recovery_days,
                AVG(resilience_score) AS avg_resilience_score
            FROM v_disruption_details
            WHERE disruption_type = :disruption_type
              AND industry = :industry
            GROUP BY response_type
            ORDER BY avg_resilience_score DESC, avg_revenue_loss ASC;
        """)

        params = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
        }

        with engine.connect() as conn:
            rows = conn.execute(benchmark_sql, params).mappings().fetchall()

            # If sparse, widen to disruption_type alone
            if len(rows) < 2:
                fallback_sql = text("""
                    SELECT 
                        response_type,
                        COUNT(*) AS incident_count,
                        AVG(revenue_loss_usd) AS avg_revenue_loss,
                        AVG(full_recovery_days) AS avg_recovery_days,
                        AVG(resilience_score) AS avg_resilience_score
                    FROM v_disruption_details
                    WHERE disruption_type = :disruption_type
                    GROUP BY response_type
                    ORDER BY avg_resilience_score DESC, avg_revenue_loss ASC;
                """)
                rows = conn.execute(fallback_sql, {"disruption_type": incident.disruption_type}).mappings().fetchall()

        benchmarks: list[StrategyComparison] = []
        for r in rows:
            benchmarks.append(
                StrategyComparison(
                    response_type=str(r["response_type"]),
                    incident_count=int(r["incident_count"]),
                    avg_revenue_loss=round(float(r["avg_revenue_loss"] or 0.0), 2),
                    avg_recovery_days=round(float(r["avg_recovery_days"] or 0.0), 1),
                    avg_resilience_score=round(float(r["avg_resilience_score"] or 0.0), 2),
                )
            )

        # Select primary (top resilience) and fallback strategies
        primary = benchmarks[0].response_type if benchmarks else "Combined Strategy"
        fallback = benchmarks[1].response_type if len(benchmarks) > 1 else "Inventory Buffer"

        # Determine Response SLA based on Triage Level
        if impact.prioritization_level == "P1-Critical":
            sla_days = 3
        elif impact.prioritization_level == "P2-High":
            sla_days = 7
        elif impact.prioritization_level == "P3-Medium":
            sla_days = 14
        else:
            sla_days = 21

        checklist = STRATEGY_CHECKLISTS.get(
            primary, STRATEGY_CHECKLISTS["Combined Strategy"]
        )

        rationale = (
            f"Based on historical analysis of {sum(b.incident_count for b in benchmarks):,} analogous cases in "
            f"{incident.industry}, '{primary}' historically achieved the highest resilience score "
            f"({benchmarks[0].avg_resilience_score:.1f}%) and an average recovery of {benchmarks[0].avg_recovery_days:.1f} days, "
            f"outperforming '{fallback}' by ${(benchmarks[1].avg_revenue_loss - benchmarks[0].avg_revenue_loss):,.2f} in financial mitigation."
            if len(benchmarks) > 1
            else f"Deploying standard empirical playbook '{primary}' for {incident.disruption_type}."
        )

        return ResponseResult(
            recommended_strategy=primary,
            fallback_strategy=fallback,
            response_sla_days=sla_days,
            strategy_benchmarks=benchmarks,
            operational_checklist=checklist,
            strategic_rationale=rationale,
        )


if __name__ == "__main__":
    from app.agents.impact_agent import ImpactAgent

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
    response_agent = ResponseAgent()
    resp_res = response_agent.plan_response(sample, impact_res)
    print("=== Response Planning Agent Test ===")
    print("Recommended:", resp_res.recommended_strategy)
    print("Fallback:", resp_res.fallback_strategy)
    print("SLA Days:", resp_res.response_sla_days)
    print("Rationale:", resp_res.strategic_rationale)
    print("Checklist steps:", len(resp_res.operational_checklist))
