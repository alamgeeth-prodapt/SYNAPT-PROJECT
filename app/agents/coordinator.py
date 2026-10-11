"""
Master Multi-Agent Workflow Coordinator.
Orchestrates the complete 5-agent pipeline:
  InvestigationAgent -> ImpactAgent -> ResponseAgent -> RecoveryAgent -> LLMJudgeAgent
Synthesizes the consolidated Executive Crisis Dossier.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.agents.schemas import (
    IncidentInput,
    ExecutiveDossier,
)
from app.agents.investigation_agent import InvestigationAgent
from app.agents.impact_agent import ImpactAgent
from app.agents.response_agent import ResponseAgent
from app.agents.recovery_agent import RecoveryAgent
from app.agents.judge import LLMJudgeAgent


class DisruptionCoordinator:
    def __init__(self):
        self.investigation_agent = InvestigationAgent()
        self.impact_agent = ImpactAgent()
        self.response_agent = ResponseAgent()
        self.recovery_agent = RecoveryAgent()
        self.judge_agent = LLMJudgeAgent()

    def process_incident(self, raw_incident: dict[str, Any] | IncidentInput) -> ExecutiveDossier:
        """
        End-to-end multi-agent orchestration for a reported supply chain disruption.
        """
        # Step 0: Input validation and guardrails
        if isinstance(raw_incident, dict):
            incident = IncidentInput(**raw_incident)
        else:
            incident = raw_incident

        now = datetime.now(timezone.utc)
        dossier_id = f"DOS-{now.strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6].upper()}"
        generated_at = now.isoformat()

        # Step 1: Investigation Agent
        investigation_result = self.investigation_agent.investigate(incident)

        # Step 2: Impact Assessment Agent
        impact_result = self.impact_agent.assess(incident)

        # Step 3: Response Planning Agent
        response_result = self.response_agent.plan_response(incident, impact_result)

        # Step 4: Recovery Analysis Agent
        recovery_result = self.recovery_agent.forecast_recovery(incident, response_result)

        # Step 5: LLM-as-Judge & Governance Validator
        judge_verdict = self.judge_agent.evaluate_plan(
            incident, impact_result, response_result, recovery_result
        )

        # Step 6: Synthesize Executive Summary
        executive_summary = (
            f"EXECUTIVE SUMMARY: {impact_result.prioritization_level} disruption detected: "
            f"a {incident.disruption_type} impacting Tier-{incident.supplier_tier} {incident.industry} "
            f"operations in {incident.supplier_region}. "
            f"ML models forecast {impact_result.predicted_production_impact_pct:.1f}% production downtime, "
            f"${impact_result.predicted_revenue_loss_usd:,.2f} estimated revenue loss, "
            f"and a composite Resilience Score of {impact_result.resilience_score:.1f}%. "
            f"Primary risk drivers: {', '.join(impact_result.top_risk_drivers)}. "
            f"Recommended empirical response is '{response_result.recommended_strategy}' "
            f"(Response SLA: {response_result.response_sla_days} days, Target Full Recovery: "
            f"{recovery_result.forecasted_full_recovery_days:.0f} days). "
            f"Governance Verdict: {judge_verdict.status} (Confidence: {judge_verdict.confidence_score:.2f})."
        )

        return ExecutiveDossier(
            dossier_id=dossier_id,
            generated_at=generated_at,
            incident=incident,
            investigation=investigation_result,
            impact=impact_result,
            response=response_result,
            recovery=recovery_result,
            judge_verdict=judge_verdict,
            executive_summary=executive_summary,
        )


if __name__ == "__main__":
    coordinator = DisruptionCoordinator()

    test_payload = {
        "disruption_type": "Cyber Attack",
        "industry": "Electronics",
        "supplier_tier": 2,
        "supplier_region": "Asia-Pacific",
        "supplier_size": "Large",
        "has_backup_supplier": False,
        "disruption_severity": 4,
    }

    print("=== Testing DisruptionCoordinator (End-to-End Multi-Agent) ===")
    dossier = coordinator.process_incident(test_payload)
    print(f"\nDossier ID: {dossier.dossier_id}")
    print(f"Prioritization: {dossier.impact.prioritization_level}")
    print(f"Resilience Score: {dossier.impact.resilience_score}%")
    print(f"Recommended Strategy: {dossier.response.recommended_strategy}")
    print(f"Forecasted Recovery Days: {dossier.recovery.forecasted_full_recovery_days}")
    print(f"Judge Verdict: {dossier.judge_verdict.status} (Confidence: {dossier.judge_verdict.confidence_score})")
    print(f"\nExecutive Summary:\n{dossier.executive_summary}")
