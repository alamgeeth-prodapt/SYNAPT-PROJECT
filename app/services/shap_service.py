"""
Phase 3: Explainable AI (SHAP) via native XGBoost TreeSHAP.

Wraps the MLService models with local feature-attribution ("waterfall")
explanations: base value + signed per-feature contributions that sum to the
model's predicted value.
"""

from typing import Any

import numpy as np
import xgboost as xgb

from app.services.ml_service import MLService


class SHAPService:
    def __init__(self, ml_service: MLService):
        self.ml_service = ml_service

    # ------------------------------------------------------------------
    # Core TreeSHAP computation
    # ------------------------------------------------------------------

    def _explain(self, model, incident: dict[str, Any], target: str) -> dict[str, Any]:
        X = self.ml_service.format_input_df(incident, target)
        booster = model.get_booster()

        dmat = xgb.DMatrix(X, enable_categorical=True)
        contribs = booster.predict(dmat, pred_contribs=True)[0]  # shape: (num_features + 1,)

        feature_names = list(X.columns)
        feature_contribs = contribs[:-1]
        base_value = float(contribs[-1])
        predicted_value = float(base_value + feature_contribs.sum())

        if target == "revenue_loss_usd":
            # Model predicts log1p(revenue_loss_usd). Transform base & prediction to USD,
            # and apportion dollar difference across features proportionally to log attributions.
            base_value_usd = max(0.0, float(np.expm1(base_value)))
            predicted_value_usd = max(0.0, float(np.expm1(predicted_value)))
            diff_usd = predicted_value_usd - base_value_usd
            diff_log = float(feature_contribs.sum())

            if abs(diff_log) > 1e-9:
                feature_contribs = (feature_contribs / diff_log) * diff_usd
            else:
                feature_contribs = np.zeros_like(feature_contribs)

            base_value = base_value_usd
            predicted_value = predicted_value_usd
            precision = 2
        else:
            precision = 4

        features = [
            {
                "name": name,
                "value": self._raw_value(X, name),
                "contribution": round(float(contrib), precision),
            }
            for name, contrib in zip(feature_names, feature_contribs)
        ]
        features.sort(key=lambda f: abs(f["contribution"]), reverse=True)

        top_risk_drivers = [
            f["name"] for f in features if f["contribution"] > 0
        ][:3]

        return {
            "target": target,
            "base_value": round(base_value, precision),
            "predicted_value": round(predicted_value, precision),
            "features": features,
            "top_risk_drivers": top_risk_drivers,
        }

    @staticmethod
    def _raw_value(X, column: str):
        value = X.at[0, column]
        # Categorical dtype values print as the underlying label (int or str).
        return value.item() if hasattr(value, "item") else value

    # ------------------------------------------------------------------
    # Public explanations
    # ------------------------------------------------------------------

    def explain_impact(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Returns feature contributions for production_impact_pct."""
        return self._explain(self.ml_service.impact_model, incident, "production_impact_pct")

    def explain_loss(self, incident: dict[str, Any], impact_pct: float | None = None) -> dict[str, Any]:
        """Returns feature contributions for revenue_loss_usd."""
        if impact_pct is None:
            impact_pct = self.ml_service.predict_impact(incident)
        incident_with_impact = {**incident, "production_impact_pct": impact_pct}
        return self._explain(self.ml_service.loss_model, incident_with_impact, "revenue_loss_usd")

    def explain_recovery(
        self, incident: dict[str, Any], scenario_overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Returns feature contributions for full_recovery_days."""
        scenario = {**incident, **(scenario_overrides or {})}
        return self._explain(self.ml_service.recovery_model, scenario, "full_recovery_days")

    def get_risk_driver_narrative(self, explanation: dict[str, Any]) -> str:
        """Generates a concise 1-sentence root-cause explanation for LLM agent context."""
        target = explanation["target"]
        drivers = explanation["top_risk_drivers"]

        if not drivers:
            return f"No single feature strongly drove the {target} prediction; contributions were broadly distributed."

        by_name = {f["name"]: f for f in explanation["features"]}
        driver_phrases = [
            f"{name} (value={by_name[name]['value']}, +{by_name[name]['contribution']:.2f})"
            for name in drivers
        ]
        return f"The {target} prediction was driven primarily by: " + ", ".join(driver_phrases) + "."


def _print_waterfall(explanation: dict[str, Any]):
    print(f"Target: {explanation['target']}")
    print(f"Base value: {explanation['base_value']}")
    print(f"Predicted value: {explanation['predicted_value']}")
    print("Feature contributions (sorted by |impact|):")
    for f in explanation["features"]:
        sign = "+" if f["contribution"] >= 0 else ""
        print(f"  {f['name']:28s} value={str(f['value']):>8s}  {sign}{f['contribution']}")
    print("Top risk drivers:", explanation["top_risk_drivers"])


if __name__ == "__main__":
    ml = MLService()
    shap_service = SHAPService(ml)

    severe_case = {
        "disruption_type": "Cyber Attack",
        "industry": "Electronics",
        "supplier_tier": 2,
        "supplier_region": "Asia-Pacific",
        "supplier_size": "Large",
        "has_backup_supplier": 0,
        "disruption_severity": 4,
    }

    print("=== SHAP explanation: production_impact_pct (severe case) ===")
    impact_explanation = shap_service.explain_impact(severe_case)
    _print_waterfall(impact_explanation)

    # Mathematical invariant: base_value + sum(contributions) == predicted_value.
    # Tolerance scales with magnitude — TreeSHAP contributions are float32, so a
    # fixed 1e-4 absolute tolerance (fine for a 0-100 scale target) is unrealistically
    # tight for a dollar-scale target like revenue_loss_usd (checked below).
    def assert_shap_invariant(explanation: dict[str, Any]):
        recomputed = explanation["base_value"] + sum(f["contribution"] for f in explanation["features"])
        predicted = explanation["predicted_value"]
        tolerance = max(0.05, abs(predicted) * 1e-4)
        assert abs(recomputed - predicted) < tolerance, (
            f"SHAP invariant violated for {explanation['target']}: {recomputed} != {predicted}"
        )

    assert_shap_invariant(impact_explanation)
    print("  [PASS] base_value + sum(contributions) == predicted_value")

    assert "disruption_severity" in impact_explanation["top_risk_drivers"] or "has_backup_supplier" in (
        impact_explanation["top_risk_drivers"]
    ), "Expected severity or backup-supplier status among top risk drivers for the severe case"
    print("  [PASS] Top risk drivers include severity and/or backup-supplier status")

    print("\nNarrative:", shap_service.get_risk_driver_narrative(impact_explanation))

    print("\n=== SHAP explanation: revenue_loss_usd (severe case) ===")
    loss_explanation = shap_service.explain_loss(severe_case)
    _print_waterfall(loss_explanation)
    assert_shap_invariant(loss_explanation)
    print("  [PASS] base_value + sum(contributions) == predicted_value")

    print("\nAll shap_service.py checks passed.")
