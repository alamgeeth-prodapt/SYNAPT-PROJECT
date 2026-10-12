"""
Impact Worker (XGBoost ML Models).
Computes predictive machine learning forecasts for downtime %, revenue loss $, and recovery days.
"""

from typing import Any
from app.agents.copilot.state import CopilotSupervisorState
from app.services.ml_service import MLService


def compute_ml_forecasts(query: str, injected_classes: dict, records: list[dict] | None = None) -> dict[str, Any]:
    try:
        ml = MLService()
        detected_type = "Factory Incident"
        detected_ind = "Automotive"
        detected_region = "Asia-Pacific"
        detected_tier = 2
        detected_severity = 3
        detected_size = "Medium"
        has_backup = False

        # 1. Match from Synapt injected classes ontology
        for col, dom in (injected_classes or {}).items():
            matched = dom.get("matched_value")
            if matched:
                if col == "disruption_type":
                    detected_type = str(matched)
                elif col == "industry":
                    detected_ind = str(matched)
                elif col == "supplier_region":
                    detected_region = str(matched)
                elif col == "supplier_tier":
                    try:
                        detected_tier = int(matched)
                    except (ValueError, TypeError):
                        pass
                elif col == "disruption_severity":
                    try:
                        detected_severity = int(matched)
                    except (ValueError, TypeError):
                        pass
                elif col == "has_backup_supplier":
                    has_backup = bool(matched)
                elif col == "supplier_size":
                    detected_size = str(matched)

        # 2. If records are available from SQL investigation, enrich missing fields
        if records and len(records) > 0:
            top_rec = records[0]
            if top_rec.get("disruption_type") and detected_type == "Factory Incident":
                detected_type = str(top_rec["disruption_type"])
            if top_rec.get("industry") and detected_ind == "Automotive":
                detected_ind = str(top_rec["industry"])
            if top_rec.get("supplier_region") and detected_region == "Asia-Pacific":
                detected_region = str(top_rec["supplier_region"])
            if top_rec.get("supplier_tier"):
                try:
                    detected_tier = int(top_rec["supplier_tier"])
                except (ValueError, TypeError):
                    pass
            if top_rec.get("disruption_severity"):
                try:
                    detected_severity = int(top_rec["disruption_severity"])
                except (ValueError, TypeError):
                    pass
            if top_rec.get("supplier_size"):
                detected_size = str(top_rec["supplier_size"])
            if "has_backup_supplier" in top_rec:
                has_backup = bool(top_rec["has_backup_supplier"])

        # 3. Categorical validation against model domain levels
        valid_types = ["Factory Incident", "Cyber Attack", "Port Congestion", "Labor Strike", "Geopolitical", "Natural Disaster"]
        valid_inds = ["Pharmaceuticals", "Electronics", "Consumer Goods", "Automotive", "Aerospace"]
        valid_regions = ["Asia-Pacific", "Europe", "South America", "North America", "Africa/Middle East"]
        valid_sizes = ["Large", "Medium", "Small"]

        if detected_type not in valid_types:
            detected_type = "Factory Incident"
        if detected_ind not in valid_inds:
            detected_ind = "Automotive"
        if detected_region not in valid_regions:
            detected_region = "Asia-Pacific"
        if detected_size not in valid_sizes:
            detected_size = "Medium"
        if detected_tier not in [1, 2, 3, 4]:
            detected_tier = 2
        if detected_severity not in [1, 2, 3, 4, 5]:
            detected_severity = 3

        incident = {
            "disruption_type": detected_type,
            "industry": detected_ind,
            "supplier_tier": detected_tier,
            "supplier_region": detected_region,
            "supplier_size": detected_size,
            "has_backup_supplier": int(has_backup),
            "disruption_severity": detected_severity,
        }

        pred_downtime = ml.predict_impact(incident)
        pred_revenue = ml.predict_revenue_loss(incident, pred_downtime)
        pred_recovery = ml.predict_recovery_days(incident)

        return {
            "detected_scenario": {
                "disruption_type": detected_type,
                "industry": detected_ind,
                "supplier_region": detected_region,
                "supplier_tier": detected_tier,
                "disruption_severity": detected_severity,
                "has_backup_supplier": has_backup,
            },
            "forecasted_downtime_pct": round(float(pred_downtime), 2),
            "forecasted_revenue_loss_usd": round(float(pred_revenue), 2),
            "forecasted_recovery_days": round(float(pred_recovery), 1),
        }
    except Exception as e:
        return {"error": f"ML inference bypassed: {str(e)}"}


async def impact_worker(state: CopilotSupervisorState) -> CopilotSupervisorState:
    query = state.get("user_query", "")
    context = state.get("agent_context", {}).copy()
    sql_res = context.get("investigation_worker", {})
    injected_classes = sql_res.get("injected_classes", {})
    records = sql_res.get("records", [])

    ml_metrics = compute_ml_forecasts(query, injected_classes, records)
    context["impact_worker"] = ml_metrics

    completed = context.get("_completed_workers", []).copy()
    if "impact_worker" not in completed:
        completed.append("impact_worker")
    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "Impact Agent (XGBoost ML Models)",
        "output": f"Downtime: {ml_metrics.get('forecasted_downtime_pct')}%, Loss: ${ml_metrics.get('forecasted_revenue_loss_usd')}",
    })

    activated = state.get("activated_agents", []).copy()
    agent_label = "Impact Agent (XGBoost ML Models)"
    if agent_label not in activated:
        activated.append(agent_label)

    return {
        **state,
        "agent_context": context,
        "execution_trace": trace,
        "activated_agents": activated,
        "ml_metrics": ml_metrics,
        "next": "supervisor",
    }
