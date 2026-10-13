"""
FastAPI Router for Supply Chain Disruption Analytics & Visualizations.
Aggregates historical data warehouse cohorts (v_disruption_details) for interactive charts.
Modeled after executive dashboard analytics architectures.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text

from app.core.database import engine
from app.core.security import User, get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["Disruption Analytics & Dashboards"])

# In-memory TTL cache for high performance
_CACHE: dict[str, dict[str, Any]] = {}
CACHE_TTL_SECONDS = 900.0


class KPISummary(BaseModel):
    total_incidents: int
    avg_production_impact_pct: float
    avg_revenue_loss_usd: float
    total_revenue_loss_usd: float
    avg_recovery_days: float
    avg_resilience_score: float
    backup_supplier_pct: float
    p1_critical_count: int


class DisruptionTypeItem(BaseModel):
    disruption_type: str
    count: int
    avg_impact_pct: float
    avg_revenue_loss_usd: float
    avg_resilience_score: float


class IndustryExposureItem(BaseModel):
    industry: str
    count: int
    avg_impact_pct: float
    avg_revenue_loss_usd: float
    avg_recovery_days: float


class SeverityBackupItem(BaseModel):
    severity: int
    has_backup_supplier: bool
    count: int
    avg_impact_pct: float
    avg_recovery_days: float
    avg_revenue_loss_usd: float


class RegionalBreakdownItem(BaseModel):
    region: str
    count: int
    avg_resilience_score: float
    avg_revenue_loss_usd: float
    avg_recovery_days: float


class ResponseEffectivenessItem(BaseModel):
    strategy: str
    count: int
    avg_recovery_days: float
    avg_revenue_loss_usd: float
    avg_response_time_days: float


class TriageDistributionItem(BaseModel):
    prioritization_level: str
    count: int
    percentage: float


class AnalyticsOverviewResponse(BaseModel):
    kpis: KPISummary
    disruption_type_distribution: list[DisruptionTypeItem]
    industry_exposure: list[IndustryExposureItem]
    severity_backup_comparison: list[SeverityBackupItem]
    regional_breakdown: list[RegionalBreakdownItem]
    response_effectiveness: list[ResponseEffectivenessItem]
    triage_distribution: list[TriageDistributionItem]
    applied_filters: dict[str, Any]
    query_time_ms: float


def _build_where_clause(industry: Any, region: Any) -> tuple[str, dict[str, Any]]:
    clauses = ["1=1"]
    params: dict[str, Any] = {}
    if isinstance(industry, str) and industry.strip() and industry.strip().lower() != "all":
        clauses.append("industry = :industry")
        params["industry"] = industry.strip()
    if isinstance(region, str) and region.strip() and region.strip().lower() != "all":
        clauses.append("supplier_region = :region")
        params["region"] = region.strip()
    return " AND ".join(clauses), params


def _fetch_kpis(where_sql: str, params: dict[str, Any]) -> tuple[KPISummary, int]:
    with engine.connect() as conn:
        kpi_sql = f"""
            SELECT
                COUNT(*) AS total_incidents,
                COALESCE(AVG(production_impact_pct), 0) AS avg_impact,
                COALESCE(AVG(revenue_loss_usd), 0) AS avg_loss,
                COALESCE(SUM(revenue_loss_usd), 0) AS sum_loss,
                COALESCE(AVG(full_recovery_days), 0) AS avg_recovery,
                COALESCE(AVG(resilience_score), 0) AS avg_resilience,
                COALESCE(SUM(CASE WHEN has_backup_supplier = 1 THEN 1 ELSE 0 END), 0) AS backup_count,
                COALESCE(SUM(CASE WHEN prioritization_level = 'P1-Critical' THEN 1 ELSE 0 END), 0) AS p1_count
            FROM v_disruption_details
            WHERE {where_sql}
        """
        kpi_row = conn.execute(text(kpi_sql), params).fetchone()
        assert kpi_row is not None
        m = kpi_row._mapping
        tot = int(m["total_incidents"])
        backup_pct = (float(m["backup_count"]) / tot * 100.0) if tot > 0 else 0.0

        return (
            KPISummary(
                total_incidents=tot,
                avg_production_impact_pct=round(float(m["avg_impact"]), 2),
                avg_revenue_loss_usd=round(float(m["avg_loss"]), 2),
                total_revenue_loss_usd=round(float(m["sum_loss"]), 2),
                avg_recovery_days=round(float(m["avg_recovery"]), 1),
                avg_resilience_score=round(float(m["avg_resilience"]), 2),
                backup_supplier_pct=round(backup_pct, 1),
                p1_critical_count=int(m["p1_count"]),
            ),
            tot,
        )


def _fetch_disruption_types(where_sql: str, params: dict[str, Any]) -> list[DisruptionTypeItem]:
    with engine.connect() as conn:
        dt_sql = f"""
            SELECT
                disruption_type,
                COUNT(*) AS cnt,
                AVG(production_impact_pct) AS avg_impact,
                AVG(revenue_loss_usd) AS avg_loss,
                AVG(resilience_score) AS avg_res
            FROM v_disruption_details
            WHERE {where_sql}
            GROUP BY disruption_type
            ORDER BY cnt DESC
        """
        dt_rows = conn.execute(text(dt_sql), params).fetchall()
        return [
            DisruptionTypeItem(
                disruption_type=r[0],
                count=int(r[1]),
                avg_impact_pct=round(float(r[2]), 2),
                avg_revenue_loss_usd=round(float(r[3]), 2),
                avg_resilience_score=round(float(r[4]), 2),
            )
            for r in dt_rows
        ]


def _fetch_industry_exposure(where_sql: str, params: dict[str, Any]) -> list[IndustryExposureItem]:
    with engine.connect() as conn:
        ind_sql = f"""
            SELECT
                industry,
                COUNT(*) AS cnt,
                AVG(production_impact_pct) AS avg_impact,
                AVG(revenue_loss_usd) AS avg_loss,
                AVG(full_recovery_days) AS avg_rec
            FROM v_disruption_details
            WHERE {where_sql}
            GROUP BY industry
            ORDER BY avg_loss DESC
        """
        ind_rows = conn.execute(text(ind_sql), params).fetchall()
        return [
            IndustryExposureItem(
                industry=r[0],
                count=int(r[1]),
                avg_impact_pct=round(float(r[2]), 2),
                avg_revenue_loss_usd=round(float(r[3]), 2),
                avg_recovery_days=round(float(r[4]), 1),
            )
            for r in ind_rows
        ]


def _fetch_severity_backup(where_sql: str, params: dict[str, Any]) -> list[SeverityBackupItem]:
    with engine.connect() as conn:
        sev_sql = f"""
            SELECT
                disruption_severity,
                has_backup_supplier,
                COUNT(*) AS cnt,
                AVG(production_impact_pct) AS avg_impact,
                AVG(full_recovery_days) AS avg_rec,
                AVG(revenue_loss_usd) AS avg_loss
            FROM v_disruption_details
            WHERE {where_sql}
            GROUP BY disruption_severity, has_backup_supplier
            ORDER BY disruption_severity ASC, has_backup_supplier ASC
        """
        sev_rows = conn.execute(text(sev_sql), params).fetchall()
        return [
            SeverityBackupItem(
                severity=int(r[0]),
                has_backup_supplier=bool(r[1]),
                count=int(r[2]),
                avg_impact_pct=round(float(r[3]), 2),
                avg_recovery_days=round(float(r[4]), 1),
                avg_revenue_loss_usd=round(float(r[5]), 2),
            )
            for r in sev_rows
        ]


def _fetch_regional_breakdown(where_sql: str, params: dict[str, Any]) -> list[RegionalBreakdownItem]:
    with engine.connect() as conn:
        reg_sql = f"""
            SELECT
                supplier_region,
                COUNT(*) AS cnt,
                AVG(resilience_score) AS avg_res,
                AVG(revenue_loss_usd) AS avg_loss,
                AVG(full_recovery_days) AS avg_rec
            FROM v_disruption_details
            WHERE {where_sql}
            GROUP BY supplier_region
            ORDER BY cnt DESC
        """
        reg_rows = conn.execute(text(reg_sql), params).fetchall()
        return [
            RegionalBreakdownItem(
                region=r[0],
                count=int(r[1]),
                avg_resilience_score=round(float(r[2]), 2),
                avg_revenue_loss_usd=round(float(r[3]), 2),
                avg_recovery_days=round(float(r[4]), 1),
            )
            for r in reg_rows
        ]


def _fetch_response_effectiveness(where_sql: str, params: dict[str, Any]) -> list[ResponseEffectivenessItem]:
    with engine.connect() as conn:
        strat_sql = f"""
            SELECT
                response_type,
                COUNT(*) AS cnt,
                AVG(full_recovery_days) AS avg_rec,
                AVG(revenue_loss_usd) AS avg_loss,
                AVG(response_time_days) AS avg_resp_time
            FROM v_disruption_details
            WHERE {where_sql}
            GROUP BY response_type
            ORDER BY avg_rec ASC
        """
        strat_rows = conn.execute(text(strat_sql), params).fetchall()
        return [
            ResponseEffectivenessItem(
                strategy=r[0],
                count=int(r[1]),
                avg_recovery_days=round(float(r[2]), 1),
                avg_revenue_loss_usd=round(float(r[3]), 2),
                avg_response_time_days=round(float(r[4]), 1),
            )
            for r in strat_rows
        ]


def _fetch_triage_distribution(where_sql: str, params: dict[str, Any]) -> list[tuple[str, int]]:
    with engine.connect() as conn:
        if where_sql == "1=1":
            triage_sql = """
                SELECT
                    prioritization_level,
                    COUNT(*) AS cnt
                FROM incident_assessments
                GROUP BY prioritization_level
                ORDER BY cnt DESC
            """
        else:
            triage_sql = f"""
                SELECT
                    prioritization_level,
                    COUNT(*) AS cnt
                FROM v_disruption_details
                WHERE {where_sql}
                GROUP BY prioritization_level
                ORDER BY cnt DESC
            """
        triage_rows = conn.execute(text(triage_sql), params).fetchall()
        return [(str(r[0]), int(r[1])) for r in triage_rows]


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get Consolidated Analytics Overview & Chart Datasets (JWT Protected)",
)
def get_analytics_overview(
    industry: str | None = Query(default=None, description="Filter by Industry"),
    region: str | None = Query(default=None, description="Filter by Supplier Region"),
    current_user: User = Depends(get_current_user),
):
    """
    Returns aggregated KPI statistics and pre-bucketed datasets for 6 visual chart panels:
    1. Overall KPI Summary
    2. Disruption Type Volume & Loss
    3. Industry Exposure & Downtime
    4. Severity vs. Backup Supplier Shield
    5. Regional Risk & Resilience Breakdown
    6. Response Strategy Recovery Timeline
    7. Triage Prioritization (P1-P4) Breakdown
    """
    ind_val = industry if isinstance(industry, str) else None
    reg_val = region if isinstance(region, str) else None
    cache_key = f"{(ind_val or 'all').lower()}_{(reg_val or 'all').lower()}"
    now = time.time()
    if cache_key in _CACHE:
        entry = _CACHE[cache_key]
        if now - entry["timestamp"] < CACHE_TTL_SECONDS:
            return entry["data"]

    try:
        t0 = time.time()
        where_sql, params = _build_where_clause(ind_val, reg_val)

        with ThreadPoolExecutor(max_workers=7) as executor:
            f_kpi = executor.submit(_fetch_kpis, where_sql, params)
            f_dt = executor.submit(_fetch_disruption_types, where_sql, params)
            f_ind = executor.submit(_fetch_industry_exposure, where_sql, params)
            f_sev = executor.submit(_fetch_severity_backup, where_sql, params)
            f_reg = executor.submit(_fetch_regional_breakdown, where_sql, params)
            f_strat = executor.submit(_fetch_response_effectiveness, where_sql, params)
            f_triage = executor.submit(_fetch_triage_distribution, where_sql, params)

            kpis, tot = f_kpi.result()
            disruption_types = f_dt.result()
            industry_exposure = f_ind.result()
            severity_backup = f_sev.result()
            regional_breakdown = f_reg.result()
            response_effectiveness = f_strat.result()
            raw_triage = f_triage.result()

        triage_distribution = [
            TriageDistributionItem(
                prioritization_level=p_level,
                count=count,
                percentage=round((count / tot * 100.0) if tot > 0 else 0.0, 1),
            )
            for p_level, count in raw_triage
        ]

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response = AnalyticsOverviewResponse(
            kpis=kpis,
            disruption_type_distribution=disruption_types,
            industry_exposure=industry_exposure,
            severity_backup_comparison=severity_backup,
            regional_breakdown=regional_breakdown,
            response_effectiveness=response_effectiveness,
            triage_distribution=triage_distribution,
            applied_filters={"industry": ind_val or "All", "region": reg_val or "All"},
            query_time_ms=elapsed_ms,
        )

        _CACHE[cache_key] = {"data": response, "timestamp": now}
        return response
    except Exception as exc:
        import traceback
        err_msg = traceback.format_exc()
        print("ERROR in get_analytics_overview:\n", err_msg)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(err_msg))
