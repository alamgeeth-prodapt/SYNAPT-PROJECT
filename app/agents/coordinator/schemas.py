"""
Pydantic Data Models and Validation Schemas for Multi-Agent Orchestration.
Defines input guardrails and structured payloads across all Phase 4 agents.
"""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# Input Incident Payload
# ==============================================================================

class IncidentInput(BaseModel):
    disruption_id: str | None = Field(default=None, description="Optional incident ID if referencing an existing record")
    disruption_type: Literal[
        "Factory Incident",
        "Cyber Attack",
        "Port Congestion",
        "Labor Strike",
        "Geopolitical",
        "Natural Disaster",
    ] = Field(description="Categorical disruption classification")
    industry: Literal[
        "Pharmaceuticals",
        "Electronics",
        "Consumer Goods",
        "Automotive",
        "Aerospace",
    ] = Field(description="Affected industry sector")
    supplier_tier: int = Field(ge=1, le=4, description="Supplier tier depth (1=direct OEM to 4=raw material)")
    supplier_region: Literal[
        "Asia-Pacific",
        "Europe",
        "South America",
        "North America",
        "Africa/Middle East",
    ] = Field(description="Geographic region of affected supplier")
    supplier_size: Literal["Large", "Medium", "Small"] = Field(
        default="Medium", description="Supplier organizational size"
    )
    has_backup_supplier: bool = Field(description="Whether a qualified second-source supplier is already in place")
    disruption_severity: int = Field(ge=1, le=5, description="Incident severity level (1=Minor to 5=Catastrophic)")

    # Optional known operational metrics at reporting time
    production_impact_pct: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Observed production downtime percentage if known"
    )
    revenue_loss_usd: float | None = Field(
        default=None, ge=0.0, description="Known financial damage in USD if already assessed"
    )
    natural_language_context: str | None = Field(
        default=None, description="Optional free-form operator notes or alert description"
    )

    @field_validator("supplier_tier", mode="before")
    @classmethod
    def parse_tier(cls, v: Any) -> int:
        if isinstance(v, str):
            digits = "".join(c for c in v if c.isdigit())
            if digits:
                return int(digits)
        return int(v)

    @field_validator("disruption_severity", mode="before")
    @classmethod
    def parse_severity(cls, v: Any) -> int:
        if isinstance(v, str):
            digits = "".join(c for c in v if c.isdigit())
            if digits:
                return int(digits)
        return int(v)

    @field_validator("supplier_region", mode="before")
    @classmethod
    def normalize_region(cls, v: Any) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            region_map = {
                "middle east": "Africa/Middle East",
                "africa": "Africa/Middle East",
                "africa/middle east": "Africa/Middle East",
                "latin america": "South America",
                "south america": "South America",
                "apac": "Asia-Pacific",
                "asia": "Asia-Pacific",
                "asia-pacific": "Asia-Pacific",
                "na": "North America",
                "north america": "North America",
                "eu": "Europe",
                "europe": "Europe",
            }
            low = v_clean.lower()
            if low in region_map:
                return region_map[low]
        return v

    @field_validator("industry", mode="before")
    @classmethod
    def normalize_industry(cls, v: Any) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            ind_map = {
                "auto": "Automotive",
                "automotive": "Automotive",
                "electronics": "Electronics",
                "chips": "Electronics",
                "semiconductors": "Electronics",
                "pharma": "Pharmaceuticals",
                "pharmaceuticals": "Pharmaceuticals",
                "consumer goods": "Consumer Goods",
                "retail": "Consumer Goods",
                "aerospace": "Aerospace",
                "aviation": "Aerospace",
                "energy": "Consumer Goods",
            }
            low = v_clean.lower()
            if low in ind_map:
                return ind_map[low]
        return v

    @field_validator("disruption_type", mode="before")
    @classmethod
    def normalize_disruption_type(cls, v: Any) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            type_map = {
                "factory": "Factory Incident",
                "factory incident": "Factory Incident",
                "fire": "Factory Incident",
                "cyber": "Cyber Attack",
                "cyber attack": "Cyber Attack",
                "ransomware": "Cyber Attack",
                "port": "Port Congestion",
                "port congestion": "Port Congestion",
                "strike": "Labor Strike",
                "labor strike": "Labor Strike",
                "geopolitical": "Geopolitical",
                "natural disaster": "Natural Disaster",
            }
            low = v_clean.lower()
            if low in type_map:
                return type_map[low]
        return v



# ==============================================================================
# Agent Output Schemas
# ==============================================================================

class InvestigationResult(BaseModel):
    incident_profile: dict[str, Any]
    cohort_filter: dict[str, Any]
    cohort_sample_size: int
    analog_cases: list[dict[str, Any]]
    cohort_benchmarks: dict[str, float]
    summary_findings: str


class ImpactResult(BaseModel):
    predicted_production_impact_pct: float
    predicted_revenue_loss_usd: float
    predicted_recovery_days: float
    resilience_score: float
    prioritization_level: Literal["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
    top_risk_drivers: list[str]
    shap_narrative: str
    feature_attributions: list[dict[str, Any]]


class StrategyComparison(BaseModel):
    response_type: str
    incident_count: int
    avg_revenue_loss: float
    avg_recovery_days: float
    avg_resilience_score: float


class ResponseResult(BaseModel):
    recommended_strategy: str
    fallback_strategy: str
    response_sla_days: int
    strategy_benchmarks: list[StrategyComparison]
    operational_checklist: list[str]
    strategic_rationale: str


class Milestone(BaseModel):
    stage: str
    target_day: int
    description: str


class RecoveryResult(BaseModel):
    forecasted_full_recovery_days: float
    permanent_supplier_change_risk_pct: float
    vendor_continuity_rating: Literal["High Risk", "Moderate Risk", "Stable"]
    milestones: list[Milestone]
    post_recovery_audit_checklist: list[str]


class JudgeVerdict(BaseModel):
    status: Literal["APPROVED", "FLAGGED_FOR_HUMAN_REVIEW"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    safety_notes: list[str]
    feasibility_notes: list[str]
    audit_summary: str


class ExecutiveDossier(BaseModel):
    dossier_id: str
    generated_at: str
    incident: IncidentInput
    investigation: InvestigationResult
    impact: ImpactResult
    response: ResponseResult
    recovery: RecoveryResult
    judge_verdict: JudgeVerdict
    executive_summary: str
