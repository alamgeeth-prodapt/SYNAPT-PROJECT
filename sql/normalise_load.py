from models import (
    Base,
    Disruption,
    Impact,
    Response,
    Recovery,
)

import pandas as pd

from sqlalchemy import text
from sqlalchemy.orm import Session

from db import engine
from models import (
    Base,
    Disruption,
    Impact,
    Response,
    Recovery,
)


CSV_PATH = r"D:\SYNAPT-PROJECT\supply_chain_disruption_recovery.csv"


REQUIRED_COLUMNS = [
    "disruption_id",
    "disruption_type",
    "industry",
    "supplier_tier",
    "supplier_region",
    "supplier_size",
    "has_backup_supplier",
    "disruption_severity",
    "production_impact_pct",
    "revenue_loss_usd",
    "response_type",
    "response_time_days",
    "partial_recovery_days",
    "full_recovery_days",
    "permanent_supplier_change",
]


def normalize_boolean(value):
    """
    Convert common CSV representations into Python booleans.
    """

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    if value in {"true", "1", "yes", "y", "t"}:
        return True

    if value in {"false", "0", "no", "n", "f"}:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Check schema
    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    # Keep only expected columns
    df = df[REQUIRED_COLUMNS].copy()

    # Strip whitespace from string columns
    string_columns = [
        "disruption_id",
        "disruption_type",
        "industry",
        "supplier_tier",
        "supplier_region",
        "supplier_size",
        "disruption_severity",
        "response_type",
    ]

    for column in string_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Boolean fields
    df["has_backup_supplier"] = (
        df["has_backup_supplier"]
        .apply(normalize_boolean)
    )

    df["permanent_supplier_change"] = (
        df["permanent_supplier_change"]
        .apply(normalize_boolean)
    )

    # Numeric fields
    numeric_columns = [
        "production_impact_pct",
        "revenue_loss_usd",
        "response_time_days",
        "partial_recovery_days",
        "full_recovery_days",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove rows without a disruption ID
    df = df.dropna(
        subset=["disruption_id"]
    )

    # Remove duplicate disruption IDs
    df = df.drop_duplicates(
        subset=["disruption_id"],
        keep="first"
    )

    return df


def validate_dataframe(df: pd.DataFrame):

    print("\nValidation")

    print(f"Rows: {len(df):,}")

    duplicate_count = df["disruption_id"].duplicated().sum()

    print(f"Duplicate IDs: {duplicate_count:,}")

    print("\nNull values:")

    nulls = df.isnull().sum()

    print(
        nulls[nulls > 0]
        .sort_values(ascending=False)
    )

    # Production impact validation
    invalid_impact = df[
        (df["production_impact_pct"] < 0)
        | (df["production_impact_pct"] > 100)
    ]

    print(
        f"\nInvalid production impact rows: "
        f"{len(invalid_impact):,}"
    )

    # Financial loss
    invalid_loss = df[
        df["revenue_loss_usd"] < 0
    ]

    print(
        f"Negative revenue loss rows: "
        f"{len(invalid_loss):,}"
    )


def load_data(df: pd.DataFrame):

    Base.metadata.create_all(engine)

    with Session(engine) as session:

        # ------------------------------------------------
        # 1. Disruptions
        # ------------------------------------------------

        disruptions = [
            Disruption(
                disruption_id=row.disruption_id,
                disruption_type=row.disruption_type,
                industry=row.industry,
                supplier_tier=row.supplier_tier,
                supplier_region=row.supplier_region,
                supplier_size=row.supplier_size,
                has_backup_supplier=row.has_backup_supplier,
                disruption_severity=row.disruption_severity,
            )
            for row in df.itertuples(index=False)
        ]

        session.bulk_save_objects(disruptions)

        # ------------------------------------------------
        # 2. Impact
        # ------------------------------------------------

        impacts = [
            Impact(
                disruption_id=row.disruption_id,
                production_impact_pct=row.production_impact_pct,
                revenue_loss_usd=row.revenue_loss_usd,
            )
            for row in df.itertuples(index=False)
        ]

        session.bulk_save_objects(impacts)

        # ------------------------------------------------
        # 3. Response
        # ------------------------------------------------

        responses = [
            Response(
                disruption_id=row.disruption_id,
                response_type=row.response_type,
                response_time_days=row.response_time_days,
            )
            for row in df.itertuples(index=False)
        ]

        session.bulk_save_objects(responses)

        # ------------------------------------------------
        # 4. Recovery
        # ------------------------------------------------

        recoveries = [
            Recovery(
                disruption_id=row.disruption_id,
                partial_recovery_days=row.partial_recovery_days,
                full_recovery_days=row.full_recovery_days,
                permanent_supplier_change=row.permanent_supplier_change,
            )
            for row in df.itertuples(index=False)
        ]

        session.bulk_save_objects(recoveries)

        session.commit()

    print("\nData successfully loaded.")


def create_view():

    with engine.begin() as connection:

        connection.execute(
            text("""
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
                    rc.permanent_supplier_change

                FROM disruptions d

                JOIN impact i
                    ON d.disruption_id = i.disruption_id

                JOIN response r
                    ON d.disruption_id = r.disruption_id

                JOIN recovery rc
                    ON d.disruption_id = rc.disruption_id
            """)
        )

    print("Created view: v_disruption_details")


def main():

    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Original rows: {len(df):,}")
    print(f"Original columns: {len(df.columns)}")

    df = clean_dataframe(df)

    validate_dataframe(df)

    load_data(df)

    create_view()


if __name__ == "__main__":
    main()