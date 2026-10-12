"""
One-off, non-destructive migration: renames the misleading `predicted_*`
columns in `incident_assessments` (which actually hold backfilled historical
ground truth, not model predictions — see populate_assessments.py) to
`baseline_*`, on both the local MySQL server and the AWS RDS instance.

Existing data is preserved — this only renames columns, it does not
touch rows. Safe to run more than once (skips a column already renamed).
"""

from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine

RENAMES = [
    ("predicted_impact_pct", "baseline_impact_pct", "DECIMAL(5,2)"),
    ("predicted_revenue_loss", "baseline_revenue_loss", "DECIMAL(15,2)"),
    ("predicted_full_recovery_days", "baseline_full_recovery_days", "INT"),
]


def rename_columns(engine: Engine, label: str):
    inspector = inspect(engine)
    existing_columns = {col["name"] for col in inspector.get_columns("incident_assessments")}

    print(f"\n[{label}] Current columns: {sorted(existing_columns)}")

    with engine.begin() as conn:
        for old_name, new_name, col_type in RENAMES:
            if old_name not in existing_columns:
                print(f"[{label}] Skipping {old_name} -> {new_name} (already renamed or absent).")
                continue

            print(f"[{label}] Renaming {old_name} -> {new_name} ...")
            conn.execute(
                text(
                    f"ALTER TABLE incident_assessments "
                    f"CHANGE COLUMN {old_name} {new_name} {col_type} NULL"
                )
            )

    inspector = inspect(engine)
    final_columns = sorted(col["name"] for col in inspector.get_columns("incident_assessments"))
    print(f"[{label}] Final columns: {final_columns}")


def main():
    from app.core.database import engine as local_engine
    rename_columns(local_engine, "LOCAL")

    import sys
    sys.path.append("sql")
    from sql.db import engine as cloud_engine
    rename_columns(cloud_engine, "CLOUD (AWS RDS)")

    print("\nMigration complete on both databases.")


if __name__ == "__main__":
    main()
