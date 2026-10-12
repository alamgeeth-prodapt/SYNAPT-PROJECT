"""
LLM-as-Judge & Governance Validator (Agent 5).
Responsible for:
  1. Evaluating the proposed response & recovery plan for operational safety.
  2. Detecting unmitigated single-point-of-failure vulnerabilities.
  3. Verifying timeline feasibility and SLA realism.
  4. Issuing formal governance verdict: APPROVED or FLAGGED_FOR_HUMAN_REVIEW.
"""

from app.agents.coordinator.schemas import (
    IncidentInput,
    ImpactResult,
    ResponseResult,
    RecoveryResult,
    JudgeVerdict,
)


class LLMJudgeAgent:
    def __init__(self):
        pass

    def evaluate_plan(
        self,
        incident: IncidentInput,
        impact: ImpactResult,
        response: ResponseResult,
        recovery: RecoveryResult,
    ) -> JudgeVerdict:
        """
        Executes multi-dimensional governance evaluation across safety,
        feasibility, and policy compliance.
        """
        safety_notes: list[str] = []
        feasibility_notes: list[str] = []
        flags: list[str] = []
        confidence_penalties: float = 0.0

        # --------------------------------------------------------------
        # 1. Safety Check: Redundancy & Single-Point-of-Failure
        # --------------------------------------------------------------
        if not incident.has_backup_supplier and incident.disruption_severity >= 4:
            if response.recommended_strategy == "Alternative Supplier":
                flags.append("NO_BACKUP_ALT_SUPPLIER_RISK")
                safety_notes.append(
                    "CRITICAL RISK: Incident has NO existing qualified backup supplier, yet primary "
                    "strategy recommends 'Alternative Supplier'. Onboarding an unqualified vendor during "
                    "a severe crisis carries significant delay and quality risk."
                )
                confidence_penalties += 0.25
            else:
                safety_notes.append(
                    "NOTICE: Unmitigated single-source dependency identified. Strategy correctly avoids "
                    "relying purely on non-existent secondary vendors."
                )

        if incident.supplier_tier in (1, 2) and impact.predicted_production_impact_pct > 60.0:
            safety_notes.append(
                f"HIGH EXPOSURE: Production downtime exceeds 60% on Tier {incident.supplier_tier} "
                "supplier; upstream bottleneck requires immediate inventory diversion."
            )

        # --------------------------------------------------------------
        # 2. Feasibility Check: SLA vs Recovery Timeline
        # --------------------------------------------------------------
        if response.response_sla_days > recovery.forecasted_full_recovery_days:
            flags.append("SLA_EXCEEDS_RECOVERY_WINDOW")
            feasibility_notes.append(
                f"TIMELINE ANOMALY: Response SLA ({response.response_sla_days} days) exceeds "
                f"forecasted full recovery window ({recovery.forecasted_full_recovery_days} days)."
            )
            confidence_penalties += 0.30
        else:
            feasibility_notes.append(
                f"SLA ALIGNMENT: Response SLA of {response.response_sla_days} days provides adequate "
                f"lead-time to execute '{response.recommended_strategy}'."
            )

        if recovery.permanent_supplier_change_risk_pct >= 40.0:
            feasibility_notes.append(
                f"VENDOR ATTRITION ALERT: High historical attrition rate ({recovery.permanent_supplier_change_risk_pct}%); "
                "procurement leadership must initiate parallel contract re-negotiation."
            )

        # --------------------------------------------------------------
        # 3. Overall Verdict Determination
        # --------------------------------------------------------------
        confidence_score = max(0.50, round(1.0 - confidence_penalties, 2))

        if flags or confidence_score < 0.80:
            status = "FLAGGED_FOR_HUMAN_REVIEW"
            audit_summary = (
                f"Plan FLAGGED for human-in-the-loop operational review. Identified {len(flags)} risk flag(s): "
                f"{', '.join(flags)}. Operator sign-off required prior to triggering ERP automated purchase orders."
            )
        else:
            status = "APPROVED"
            audit_summary = (
                f"Plan APPROVED. The empirical strategy '{response.recommended_strategy}' satisfies all "
                f"operational safety constraints for a {impact.prioritization_level} incident. "
                f"Confidence score: {confidence_score:.2f}."
            )

        return JudgeVerdict(
            status=status,
            confidence_score=confidence_score,
            safety_notes=safety_notes,
            feasibility_notes=feasibility_notes,
            audit_summary=audit_summary,
        )


if __name__ == "__main__":
    from app.agents.impact_agent import ImpactAgent
    from app.agents.response_agent import ResponseAgent
    from app.agents.recovery_agent import RecoveryAgent

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
    recovery_res = RecoveryAgent().forecast_recovery(sample, response_res)
    judge = LLMJudgeAgent()
    verdict = judge.evaluate_plan(sample, impact_res, response_res, recovery_res)

    print("=== LLM Judge Test ===")
    print("Verdict:", verdict.status)
    print("Confidence:", verdict.confidence_score)
    print("Summary:", verdict.audit_summary)
    print("Safety notes:", len(verdict.safety_notes))
