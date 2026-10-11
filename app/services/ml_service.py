"""
Phase 3: Predictive ML Engine.

Loads the 3 pre-trained XGBoost regressors from `models/` and exposes
chained inference (impact -> revenue loss -> recovery days), plus the
composite Resilience Score and P1-P4 prioritization triage, for a single
incoming disruption incident.

Deviation from PHASE_3_INSTRUCTIONS.md, verified empirically before writing
this module: the doc's feature spec lists `supplier_tier` and
`disruption_severity` as categorical STRINGS (e.g. '1'..'4'). The models
were actually trained with these as categorical INTEGERS (1..4 / 1..5) —
see preprocessing&training/02_train_models.ipynb. Feeding string categories
at inference doesn't just give wrong answers, it raises
`XGBoostError: ... category index type mismatch`. This module uses integer
categories throughout, matching what was actually trained.
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from xgboost import XGBRegressor

MODELS_DIR = Path("models")

# Controlled categories, matching training (preprocessing&training/02_train_models.ipynb)
# and the domain vocabulary in app/services/sql_builder.py.
CATEGORY_LEVELS: dict[str, list] = {
    "disruption_type": [
        "Factory Incident",
        "Cyber Attack",
        "Port Congestion",
        "Labor Strike",
        "Geopolitical",
        "Natural Disaster",
    ],
    "industry": ["Pharmaceuticals", "Electronics", "Consumer Goods", "Automotive", "Aerospace"],
    "supplier_region": [
        "Asia-Pacific",
        "Europe",
        "South America",
        "North America",
        "Africa/Middle East",
    ],
    "supplier_size": ["Large", "Medium", "Small"],
    "response_type": [
        "Customer Delay",
        "Alternative Supplier",
        "Production Reroute",
        "Inventory Buffer",
        "Combined Strategy",
    ],
    # Trained as integer categories, NOT strings — see module docstring.
    "supplier_tier": [1, 2, 3, 4],
    "disruption_severity": [1, 2, 3, 4, 5],
}

BOOLEAN_COLUMNS = ["has_backup_supplier", "permanent_supplier_change"]
INT_COLUMNS = ["response_time_days", "partial_recovery_days"]

# Defaults for response/recovery-stage fields when a caller only wants a
# pre-response forecast (e.g. predict_impact/predict_revenue_loss on their own).
RESPONSE_DEFAULTS = {
    "response_type": "Combined Strategy",
    "response_time_days": 10,
    "partial_recovery_days": 14,
    "permanent_supplier_change": 0,
}


class MLServiceError(ValueError):
    pass


class MLService:
    def __init__(self, models_dir: str = "models"):
        models_dir = Path(models_dir)

        self.impact_model = XGBRegressor()
        self.impact_model.load_model(models_dir / "production_impact_pct_model.json")

        self.loss_model = XGBRegressor()
        self.loss_model.load_model(models_dir / "revenue_loss_usd_model.json")

        self.recovery_model = XGBRegressor()
        self.recovery_model.load_model(models_dir / "full_recovery_days_model.json")

        with open(models_dir / "metrics.json") as f:
            self.metrics = json.load(f)

    # ------------------------------------------------------------------
    # Step 1: Feature validation & formatting
    # ------------------------------------------------------------------

    def format_input_df(self, incident: dict[str, Any], target: str) -> pd.DataFrame:
        """
        Converts an incident dict into a 1-row DataFrame matching the exact
        feature schema and dtypes the given target's model was trained on.
        Missing response/recovery fields fall back to RESPONSE_DEFAULTS.
        """
        features = self.metrics[target]["features"]

        row = {}
        for col in features:
            value = incident.get(col, RESPONSE_DEFAULTS.get(col))
            if value is None:
                raise MLServiceError(f"Missing required field '{col}' for target '{target}'.")
            row[col] = value

        df = pd.DataFrame([row])

        for col, levels in CATEGORY_LEVELS.items():
            if col not in df.columns:
                continue
            if col in ("supplier_tier", "disruption_severity"):
                df[col] = df[col].astype(int)
            if df.at[0, col] not in levels:
                raise MLServiceError(f"Invalid value '{df.at[0, col]}' for '{col}'. Expected one of {levels}.")
            df[col] = pd.Categorical(df[col], categories=levels)

        for col in BOOLEAN_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype(int)

        for col in INT_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype(int)

        if "production_impact_pct" in df.columns:
            df["production_impact_pct"] = df["production_impact_pct"].astype(float)

        return df[features]

    # ------------------------------------------------------------------
    # Step 2: Chained inference
    # ------------------------------------------------------------------

    def predict_impact(self, incident: dict[str, Any]) -> float:
        """Forecasts production_impact_pct (0.0 to 100.0)."""
        X = self.format_input_df(incident, "production_impact_pct")
        return float(self.impact_model.predict(X)[0])

    def predict_revenue_loss(self, incident: dict[str, Any], impact_pct: float | None = None) -> float:
        """Forecasts revenue_loss_usd. Uses predict_impact() if impact_pct isn't supplied."""
        if impact_pct is None:
            impact_pct = self.predict_impact(incident)

        incident_with_impact = {**incident, "production_impact_pct": impact_pct}
        X = self.format_input_df(incident_with_impact, "revenue_loss_usd")
        return float(self.loss_model.predict(X)[0])

    def predict_recovery_days(
        self, incident: dict[str, Any], scenario_overrides: dict[str, Any] | None = None
    ) -> float:
        """
        Forecasts full_recovery_days. `scenario_overrides` can supply/replace
        response_type, response_time_days, partial_recovery_days, or
        permanent_supplier_change to simulate a specific response strategy.
        """
        scenario = {**incident, **(scenario_overrides or {})}
        X = self.format_input_df(scenario, "full_recovery_days")
        return float(self.recovery_model.predict(X)[0])

    # ------------------------------------------------------------------
    # Step 3: Composite Resilience Score & Prioritization
    # ------------------------------------------------------------------

    @staticmethod
    def compute_resilience_score(
        full_recovery_days: float,
        revenue_loss_usd: float,
        has_backup_supplier: bool,
        severity: int,
    ) -> float:
        norm_recovery = min(1.0, full_recovery_days / 120.0)
        norm_loss = min(1.0, revenue_loss_usd / 100_000_000.0)
        backup_bonus = 1.0 if has_backup_supplier else 0.0
        penalty = 1.0 if (severity >= 4 and not has_backup_supplier) else 0.0

        raw_score = (
            0.4 * (1 - norm_recovery)
            + 0.4 * (1 - norm_loss)
            + 0.1 * backup_bonus
            - 0.1 * penalty
        ) * 100.0

        return round(max(0.0, min(100.0, raw_score)), 2)

    @staticmethod
    def compute_prioritization_level(severity: int, impact_pct: float, revenue_loss_usd: float) -> str:
        if severity >= 4 and (impact_pct > 50.0 or revenue_loss_usd > 5_000_000.0):
            return "P1-Critical"
        if severity >= 3 and (impact_pct > 35.0 or revenue_loss_usd > 1_000_000.0):
            return "P2-High"
        if severity <= 2 and impact_pct < 20.0:
            return "P4-Low"
        return "P3-Medium"

    # ------------------------------------------------------------------
    # End-to-end assessment
    # ------------------------------------------------------------------

    def assess_incident(
        self, incident: dict[str, Any], scenario_overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        End-to-end evaluation: chained predictions, resilience score, and
        prioritization level for a single incident.
        """
        severity = int(incident["disruption_severity"])
        has_backup = bool(incident["has_backup_supplier"])

        impact_pct = self.predict_impact(incident)
        revenue_loss = self.predict_revenue_loss(incident, impact_pct=impact_pct)
        recovery_days = self.predict_recovery_days(incident, scenario_overrides=scenario_overrides)

        resilience_score = self.compute_resilience_score(
            full_recovery_days=recovery_days,
            revenue_loss_usd=revenue_loss,
            has_backup_supplier=has_backup,
            severity=severity,
        )
        prioritization_level = self.compute_prioritization_level(severity, impact_pct, revenue_loss)

        return {
            "incident": incident,
            "predicted_impact_pct": round(impact_pct, 2),
            "predicted_revenue_loss_usd": round(revenue_loss, 2),
            "predicted_full_recovery_days": round(recovery_days, 1),
            "resilience_score": resilience_score,
            "prioritization_level": prioritization_level,
        }


def _print_case(ml: "MLService", label: str, incident: dict):
    print(f"\n=== {label} ===")
    print("Input:", incident)
    result = ml.assess_incident(incident)
    for key, value in result.items():
        if key == "incident":
            continue
        print(f"  {key}: {value}")
    return result


if __name__ == "__main__":
    ml = MLService()

    severe_case = {
        "disruption_type": "Cyber Attack",
        "industry": "Electronics",
        "supplier_tier": 2,
        "supplier_region": "Asia-Pacific",
        "supplier_size": "Large",
        "has_backup_supplier": 0,
        "disruption_severity": 4,
    }
    severe_result = _print_case(ml, "Severe Incident Case", severe_case)
    assert severe_result["prioritization_level"] == "P1-Critical", "Expected P1-Critical for severe case"
    assert severe_result["predicted_impact_pct"] > 50.0, "Expected downtime > 50% for severe case"
    print("  [PASS] Severe case matches expected P1-Critical, downtime > 50%")

    mild_case = {
        "disruption_type": "Port Congestion",
        "industry": "Consumer Goods",
        "supplier_tier": 1,
        "supplier_region": "North America",
        "supplier_size": "Medium",
        "has_backup_supplier": 1,
        "disruption_severity": 1,
    }
    mild_result = _print_case(ml, "Mild Incident Case", mild_case)
    assert mild_result["prioritization_level"] in ("P3-Medium", "P4-Low"), "Expected P3/P4 for mild case"
    print("  [PASS] Mild case matches expected P3-Medium/P4-Low")

    print("\nAll ml_service.py checks passed.")
