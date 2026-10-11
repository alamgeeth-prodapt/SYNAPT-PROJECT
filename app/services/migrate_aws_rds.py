"""
Migration & Sync Script for AWS RDS MySQL (`Supply_Chain`).
Creates `incident_assessments` table, populates 100k computed records,
and updates the `v_disruption_details` unified view on AWS RDS.
"""

import sys
import time
from pathlib import Path
import pandas as pd
from sqlalchemy import text

sys.path.append("sql")
from sql.db import engine
from app.services.populate_assessments import compute_assessments, DATA_PATH


def main():
    start_time = time.time()
    print("Connecting to AWS RDS MySQL...")

    with engine.connect() as conn:
        print("Connected to AWS RDS successfully.")

    # 1. Create incident_assessments table
    print("Creating `incident_assessments` table on AWS RDS...")
    ddl = text(
        """
        CREATE TABLE IF NOT EXISTS incident_assessments (
            assessment_id INT AUTO_INCREMENT PRIMARY KEY,
            disruption_id VARCHAR(100),
            baseline_impact_pct DECIMAL(5,2),
            baseline_revenue_loss DECIMAL(15,2),
            baseline_full_recovery_days INT,
            resilience_score DECIMAL(5,2),
            prioritization_level VARCHAR(20),
            supplier_change_risk DECIMAL(4,2),
            top_risk_driver VARCHAR(255),
            recommended_strategy VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_disruption_id (disruption_id)
        );
        """
    )
    with engine.begin() as conn:
        conn.execute(ddl)
    print("`incident_assessments` table verified on AWS RDS.")

    # 2. Check row count and populate if needed
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM incident_assessments")).scalar()
        print(f"Current rows in AWS RDS `incident_assessments`: {count:,}")

    if count < 100_000:
        print(f"Reading clean dataset from {DATA_PATH}...")
        df_clean = pd.read_parquet(DATA_PATH)
        assessments_df = compute_assessments(df_clean)

        print(f"Inserting {len(assessments_df):,} rows into AWS RDS in chunks of 5,000...")
        assessments_df.to_sql(
            name="incident_assessments",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )
        print("Batch insertion into AWS RDS completed!")

    # 3. Update unified view v_disruption_details on AWS RDS
    print("Updating `v_disruption_details` view on AWS RDS...")
    view_sql = text(
        """
        CREATE OR REPLACE VIEW v_disruption_details AS
        SELECT
            d.disruption_id,
            d.disruption_type,
            d.industry,
            d.supplier_tier,
            d.supplier_region,
            d.supplier_size,
            d.has_backup_supplier,
            d.disruption_severity,

            i.production_impact_pct,
            i.revenue_loss_usd,

            r.response_type,
            r.response_time_days,

            rc.partial_recovery_days,
            rc.full_recovery_days,
            rc.permanent_supplier_change,

            ia.resilience_score,
            ia.prioritization_level,
            ia.top_risk_driver,
            ia.recommended_strategy

        FROM disruptions d
        JOIN impact i ON d.disruption_id = i.disruption_id
        JOIN response r ON d.disruption_id = r.disruption_id
        JOIN recovery rc ON d.disruption_id = rc.disruption_id
        LEFT JOIN incident_assessments ia ON d.disruption_id = ia.disruption_id;
        """
    )
    with engine.begin() as conn:
        conn.execute(view_sql)
    print("`v_disruption_details` view updated on AWS RDS successfully!")

    # 4. Final verification query
    with engine.connect() as conn:
        total_assessments = conn.execute(text("SELECT COUNT(*) FROM incident_assessments")).scalar()
        print(f"\nFinal count in AWS RDS `incident_assessments`: {total_assessments:,}")

        sample = conn.execute(
            text(
                """
                SELECT disruption_id, disruption_type, supplier_tier,
                       resilience_score, prioritization_level, top_risk_driver, recommended_strategy
                FROM v_disruption_details LIMIT 3;
                """
            )
        )
        print("\nVerification sample from AWS RDS `v_disruption_details`:")
        for row in sample:
            print(" ", dict(row._mapping))

    elapsed = time.time() - start_time
    print(f"\nAWS RDS sync completed successfully in {elapsed:.2f}s!")


if __name__ == "__main__":
    main()
