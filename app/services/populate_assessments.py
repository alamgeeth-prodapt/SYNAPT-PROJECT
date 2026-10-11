"""
Batch population script for `incident_assessments` table in MySQL (`supply_chain_db`).
Computes ground-truth baseline resilience scores (using Kaggle formula),
prioritization triage levels, top risk drivers, and strategic recommendations
across the 100,000 historical disruption records.
"""

import time
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import text
from app.services.db_service import engine, init_assessment_table

DATA_PATH = Path("data/processed/disruptions_clean.parquet")


def compute_assessments(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Loaded {len(df):,} records from {DATA_PATH}. Computing metrics...")

    # 1. Recovery Score (normalized inverted full recovery days)
    rec_min = df["full_recovery_days"].min()
    rec_max = df["full_recovery_days"].max()
    recovery_norm = (df["full_recovery_days"] - rec_min) / (rec_max - rec_min)
    recovery_score = 1.0 - recovery_norm

    # 2. Impact Containment Score (normalized inverted revenue loss)
    loss_min = df["revenue_loss_usd"].min()
    loss_max = df["revenue_loss_usd"].max()
    loss_norm = (df["revenue_loss_usd"] - loss_min) / (loss_max - loss_min)
    impact_score = 1.0 - loss_norm

    # 3. Redundancy & Structural Penalty
    redundancy_score = df["has_backup_supplier"].astype(int)
    structural_penalty = df["permanent_supplier_change"].astype(int)

    # 4. Composite Resilience Score (Kaggle formula, scaled 0 - 100)
    raw_resilience = (
        0.4 * recovery_score
        + 0.4 * impact_score
        + 0.1 * redundancy_score
        - 0.1 * structural_penalty
    ) * 100.0
    resilience_score = np.clip(raw_resilience, 0.0, 100.0).round(2)

    # 5. Prioritization Triage Level
    severity = df["disruption_severity"].astype(int)
    impact_pct = df["production_impact_pct"]
    revenue_loss = df["revenue_loss_usd"]

    p1_mask = (severity >= 4) & ((impact_pct > 50.0) | (revenue_loss > 5_000_000))
    p2_mask = (~p1_mask) & (severity >= 3) & ((impact_pct > 35.0) | (revenue_loss > 1_000_000))
    p4_mask = (~p1_mask) & (~p2_mask) & (severity <= 2) & (impact_pct < 20.0)

    prioritization = np.select(
        [p1_mask, p2_mask, p4_mask],
        ["P1-Critical", "P2-High", "P4-Low"],
        default="P3-Medium",
    )

    # 6. Top Risk Driver
    no_backup = ~df["has_backup_supplier"]
    is_tier1 = df["supplier_tier"].astype(int) == 1

    driver_conditions = [
        no_backup & (severity >= 4),
        severity >= 5,
        no_backup,
        is_tier1 & (revenue_loss > 3_000_000),
        df["permanent_supplier_change"].astype(bool),
    ]
    driver_choices = [
        "No Backup Supplier & Extreme Severity",
        "Catastrophic Disruption Severity (Level 5)",
        "Lack of Redundant Backup Supplier",
        "Tier-1 Single Point of Failure",
        "High Supplier Relationship Instability",
    ]
    top_risk_driver = np.select(
        driver_conditions,
        driver_choices,
        default="Standard Operational Bottleneck",
    )

    # 7. Strategic Playbook Recommendation
    strategy_map = {
        "Cyber Attack": "Alternative Supplier",
        "Natural Disaster": "Production Reroute",
        "Port Congestion": "Customer Delay",
        "Labor Strike": "Combined Strategy",
        "Factory Incident": "Production Reroute",
        "Geopolitical": "Alternative Supplier",
    }
    recommended_strategy = df["disruption_type"].map(strategy_map).fillna("Combined Strategy")

    # Construct the output table DataFrame
    assessments_df = pd.DataFrame(
        {
            "disruption_id": df["disruption_id"].astype(str),
            "baseline_impact_pct": df["production_impact_pct"].round(2),
            "baseline_revenue_loss": df["revenue_loss_usd"].round(2),
            "baseline_full_recovery_days": df["full_recovery_days"].astype(int),
            "resilience_score": resilience_score,
            "prioritization_level": prioritization,
            "supplier_change_risk": np.where(df["permanent_supplier_change"], 1.0, 0.0),
            "top_risk_driver": top_risk_driver,
            "recommended_strategy": recommended_strategy,
        }
    )

    return assessments_df


def main():
    start_time = time.time()
    init_assessment_table()

    # Check existing count
    with engine.connect() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM incident_assessments")).scalar()
        print(f"Current rows in `incident_assessments`: {existing:,}")
        if existing > 0:
            print("Truncating table for clean population...")
            conn.execute(text("TRUNCATE TABLE incident_assessments"))

    df_clean = pd.read_parquet(DATA_PATH)
    assessments_df = compute_assessments(df_clean)

    print(f"Inserting {len(assessments_df):,} rows in chunks of 5,000...")
    assessments_df.to_sql(
        name="incident_assessments",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    elapsed = time.time() - start_time
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM incident_assessments")).scalar()
        print(f"Successfully loaded {total:,} rows into `incident_assessments` in {elapsed:.2f}s!")

        # Sample preview
        print("\nSample records:")
        sample = conn.execute(text("SELECT * FROM incident_assessments LIMIT 3"))
        for row in sample:
            print(dict(row._mapping))


if __name__ == "__main__":
    main()
