"""
Database connector for the locally-hosted MySQL `supply_chain_db`.

This is separate from `sql/db.py`, which connects to the AWS RDS / Synapt
instance over SSL. This module targets the local MySQL server where the
normalized tables (`disruptions`, `impact`, `response`, `recovery`) and the
`v_disruption_details` view already exist (loaded via sql/normalise_load.py
or an equivalent local load).

Required environment variables (add to `.env`):
    DB_HOST       e.g. "localhost" or "127.0.0.1"
    DB_PORT       e.g. "3306" (optional, defaults to 3306)
    DB_USER       local MySQL username
    DB_PASSWORD   local MySQL password

DB_NAME is fixed to "supply_chain_db" per the system architecture doc.
"""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_NAME = "supply_chain_db"

if not all([DB_HOST, DB_USER, DB_PASS]):
    raise RuntimeError(
        "Missing local MySQL settings in .env: "
        "DB_HOST, DB_USER, and DB_PASSWORD are required."
    )

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Local server, no SSL/CA cert required (unlike the AWS RDS connector in sql/db.py).
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@contextmanager
def get_session():
    """Yield a SQLAlchemy session, committing/rolling back and closing automatically."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Quick connectivity check — returns True if the DB responds to SELECT 1."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def fetch_disruption_details(filters: dict | None = None, limit: int = 100):
    """
    Read-only query against `v_disruption_details` with optional equality filters,
    e.g. {"disruption_type": "Cyber Attack", "supplier_tier": 1}.
    Uses parameter binding throughout — no string-built SQL.
    """
    filters = filters or {}

    where_clause = ""
    if filters:
        conditions = " AND ".join(f"{column} = :{column}" for column in filters)
        where_clause = f"WHERE {conditions}"

    query = text(
        f"""
        SELECT *
        FROM v_disruption_details
        {where_clause}
        LIMIT :limit
        """
    )

    with engine.connect() as conn:
        result = conn.execute(query, {**filters, "limit": limit})
        return [dict(row._mapping) for row in result]


def fetch_response_benchmarks(disruption_type: str, supplier_tier: int):
    """
    Aggregate response-strategy benchmarks for a given disruption type/tier,
    matching the Response Planning Agent query in the architecture doc.
    """
    query = text(
        """
        SELECT response_type,
               AVG(response_time_days) AS avg_response_time,
               AVG(production_impact_pct) AS avg_downtime,
               AVG(revenue_loss_usd) AS avg_financial_loss,
               AVG(full_recovery_days) AS avg_recovery_days
        FROM v_disruption_details
        WHERE disruption_type = :disruption_type AND supplier_tier = :supplier_tier
        GROUP BY response_type
        ORDER BY avg_financial_loss ASC
        """
    )

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {"disruption_type": disruption_type, "supplier_tier": supplier_tier},
        )
        return [dict(row._mapping) for row in result]


def init_assessment_table() -> bool:
    """Create the incident_assessments table if it does not already exist."""
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
        )
        """
    )
    with engine.begin() as conn:
        conn.execute(ddl)
    return True


def save_incident_assessment(assessment: dict) -> int:
    """
    Insert a newly generated disruption risk assessment record.
    Returns the newly generated assessment_id.
    """
    insert_sql = text(
        """
        INSERT INTO incident_assessments (
            disruption_id,
            baseline_impact_pct,
            baseline_revenue_loss,
            baseline_full_recovery_days,
            resilience_score,
            prioritization_level,
            supplier_change_risk,
            top_risk_driver,
            recommended_strategy
        ) VALUES (
            :disruption_id,
            :baseline_impact_pct,
            :baseline_revenue_loss,
            :baseline_full_recovery_days,
            :resilience_score,
            :prioritization_level,
            :supplier_change_risk,
            :top_risk_driver,
            :recommended_strategy
        )
        """
    )
    with engine.begin() as conn:
        result = conn.execute(insert_sql, assessment)
        return result.lastrowid


def fetch_assessments(disruption_id: str | None = None, limit: int = 50) -> list[dict]:
    """Retrieve logged assessments, optionally filtered by disruption_id."""
    if disruption_id:
        query = text(
            """
            SELECT * FROM incident_assessments
            WHERE disruption_id = :disruption_id
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )
        params = {"disruption_id": disruption_id, "limit": limit}
    else:
        query = text(
            """
            SELECT * FROM incident_assessments
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )
        params = {"limit": limit}

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result]


def update_disruption_view() -> bool:
    """
    Update or recreate the unified view `v_disruption_details` to include
    the engineered risk fields from `incident_assessments`.
    """
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
    return True


if __name__ == "__main__":
    test_connection()
    print(f"Connected to local MySQL `{DB_NAME}` at {DB_HOST}:{DB_PORT}.")
    init_assessment_table()
    print("Table `incident_assessments` checked / created successfully.")
    update_disruption_view()
    print("View `v_disruption_details` updated successfully with resilience and risk fields.")


