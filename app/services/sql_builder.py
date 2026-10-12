"""
Synapt SQL Builder Service.
Implements the 2-step decoupled architecture:
  1. Schema Selection: Inspects schema structure and selects relevant columns.
  2. Just-In-Time Value Injection: Pulls classes ONLY for selected columns.
  3. Safe SQL Synthesis: Constructs grounded read-only SELECT queries on `v_disruption_details`.
  4. Guardrails & Execution: Validates safety and executes against MySQL (`supply_chain_db`).
"""

import asyncio
import json
import os
import re
import time
from typing import Any
from sqlalchemy import text
from app.core.database import engine
from app.services.synapt_service import SynaptService

# ==============================================================================
# Domain Dictionary & Controlled Vocabularies (from supply_chain_data_dictionary)
# ==============================================================================

COLUMN_DOMAINS: dict[str, dict[str, Any]] = {
    "disruption_type": {
        "type": "categorical",
        "classes": [
            "Factory Incident",
            "Cyber Attack",
            "Port Congestion",
            "Labor Strike",
            "Geopolitical",
            "Natural Disaster",
        ],
        "synonyms": {
            "malware": "Cyber Attack",
            "ransomware": "Cyber Attack",
            "phishing": "Cyber Attack",
            "cyber": "Cyber Attack",
            "hack": "Cyber Attack",
            "ddos": "Cyber Attack",
            "fire": "Factory Incident",
            "explosion": "Factory Incident",
            "breakdown": "Factory Incident",
            "equipment failure": "Factory Incident",
            "plant fire": "Factory Incident",
            "port": "Port Congestion",
            "shipping delay": "Port Congestion",
            "harbor": "Port Congestion",
            "container backlog": "Port Congestion",
            "dock": "Port Congestion",
            "strike": "Labor Strike",
            "walkout": "Labor Strike",
            "union dispute": "Labor Strike",
            "labor": "Labor Strike",
            "sanctions": "Geopolitical",
            "tariff": "Geopolitical",
            "embargo": "Geopolitical",
            "export control": "Geopolitical",
            "trade war": "Geopolitical",
            "earthquake": "Natural Disaster",
            "typhoon": "Natural Disaster",
            "flood": "Natural Disaster",
            "tsunami": "Natural Disaster",
            "hurricane": "Natural Disaster",
            "storm": "Natural Disaster",
        },
    },
    "industry": {
        "type": "categorical",
        "classes": [
            "Pharmaceuticals",
            "Electronics",
            "Consumer Goods",
            "Automotive",
            "Aerospace",
        ],
        "synonyms": {
            "pharma": "Pharmaceuticals",
            "drug": "Pharmaceuticals",
            "drugs": "Pharmaceuticals",
            "medicine": "Pharmaceuticals",
            "vaccine": "Pharmaceuticals",
            "biotech": "Pharmaceuticals",
            "semiconductor": "Electronics",
            "microchip": "Electronics",
            "chips": "Electronics",
            "chip": "Electronics",
            "hardware": "Electronics",
            "pcb": "Electronics",
            "auto": "Automotive",
            "car": "Automotive",
            "cars": "Automotive",
            "vehicle": "Automotive",
            "ev": "Automotive",
            "carmaker": "Automotive",
            "aircraft": "Aerospace",
            "aviation": "Aerospace",
            "avionics": "Aerospace",
            "defense": "Aerospace",
            "retail": "Consumer Goods",
            "fmcg": "Consumer Goods",
            "packaged goods": "Consumer Goods",
            "apparel": "Consumer Goods",
        },
    },
    "supplier_tier": {
        "type": "ordinal",
        "classes": [1, 2, 3, 4],
        # Bare digits (e.g. "4" in "show 4 disruptions") must not be read as a
        # tier value unless one of these cue words also appears in the query.
        "numeric_cue_words": ["tier"],
        "synonyms": {
            "tier 1": 1,
            "tier-1": 1,
            "tier 2": 2,
            "tier-2": 2,
            "tier 3": 3,
            "tier-3": 3,
            "tier 4": 4,
            "tier-4": 4,
            "direct supplier": 1,
            "oem supplier": 1,
            "sub-assembly": 2,
            "raw material": 4,
            "upstream": 4,
        },
    },
    "supplier_region": {
        "type": "categorical",
        "classes": [
            "Asia-Pacific",
            "Europe",
            "South America",
            "North America",
            "Africa/Middle East",
        ],
        "synonyms": {
            "apac": "Asia-Pacific",
            "asia": "Asia-Pacific",
            "china": "Asia-Pacific",
            "taiwan": "Asia-Pacific",
            "japan": "Asia-Pacific",
            "korea": "Asia-Pacific",
            "india": "Asia-Pacific",
            "singapore": "Asia-Pacific",
            "europe": "Europe",
            "eu": "Europe",
            "germany": "Europe",
            "uk": "Europe",
            "france": "Europe",
            "italy": "Europe",
            "north america": "North America",
            "usa": "North America",
            "us": "North America",
            "united states": "North America",
            "canada": "North America",
            "mexico": "North America",
            "south america": "South America",
            "brazil": "South America",
            "latin america": "South America",
            "middle east": "Africa/Middle East",
            "uae": "Africa/Middle East",
            "saudi": "Africa/Middle East",
            "africa": "Africa/Middle East",
            "mena": "Africa/Middle East",
        },
    },
    "supplier_size": {
        "type": "categorical",
        "classes": ["Large", "Medium", "Small"],
        "synonyms": {
            "large": "Large",
            "big": "Large",
            "medium": "Medium",
            "mid-sized": "Medium",
            "small": "Small",
        },
    },
    "disruption_severity": {
        "type": "ordinal",
        "classes": [1, 2, 3, 4, 5],
        # Same guard as supplier_tier — see note there.
        "numeric_cue_words": ["severity", "level"],
        "synonyms": {
            "catastrophic": 5,
            "critical": 5,
            "level 5": 5,
            "severe": 4,
            "level 4": 4,
            "moderate": 3,
            "medium": 3,
            "level 3": 3,
            "low": 2,
            "minor": 1,
        },
    },
    "response_type": {
        "type": "categorical",
        "classes": [
            "Customer Delay",
            "Alternative Supplier",
            "Production Reroute",
            "Inventory Buffer",
            "Combined Strategy",
        ],
        "synonyms": {
            "alternative supplier": "Alternative Supplier",
            "alt supplier": "Alternative Supplier",
            "second source": "Alternative Supplier",
            "secondary supplier": "Alternative Supplier",
            "production reroute": "Production Reroute",
            "reroute": "Production Reroute",
            "divert production": "Production Reroute",
            "inventory buffer": "Inventory Buffer",
            "safety stock": "Inventory Buffer",
            "buffer": "Inventory Buffer",
            "customer delay": "Customer Delay",
            "delay fulfillment": "Customer Delay",
            "combined strategy": "Combined Strategy",
            "hybrid": "Combined Strategy",
        },
    },
    "prioritization_level": {
        "type": "categorical",
        "classes": ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"],
        "synonyms": {
            "p1": "P1-Critical",
            "p1-critical": "P1-Critical",
            "p2": "P2-High",
            "p2-high": "P2-High",
            "p3": "P3-Medium",
            "p4": "P4-Low",
        },
    },
    "has_backup_supplier": {
        "type": "boolean",
        "classes": [True, False],
        "synonyms": {
            "without backup supplier": False,
            "no backup supplier": False,
            "without backup": False,
            "no backup": False,
            "with backup supplier": True,
            "has backup supplier": True,
            "has backup": True,
            "with backup": True,
        },
    },
}

ALLOWED_TABLES = {
    "v_disruption_details",
    "disruptions",
    "impact",
    "response",
    "recovery",
    "incident_assessments",
}

FORBIDDEN_SQL_KEYWORDS = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "REPLACE",
}


class SQLSecurityException(ValueError):
    pass


def has_word(pattern: str, text: str) -> bool:
    """Case-insensitive exact word boundary match to prevent false substring hits."""
    return bool(re.search(rf"\b{re.escape(pattern.strip().lower())}\b", text.lower()))


def match_domain_value(col: str, meta: dict[str, Any], query: str) -> Any:
    """
    Find the value (if any) that `query` grounds column `col` to, checking
    classes first, then synonyms.

    For purely numeric class lists (ordinal columns like supplier_tier,
    disruption_severity), a bare digit in free text (e.g. the "4" in "show 4
    disruptions") is NOT enough on its own — it must appear alongside one of
    that column's `numeric_cue_words` (e.g. "tier", "severity"), otherwise
    unrelated numbers (counts, "top N", years) would misfire as filters.
    Textual synonyms (e.g. "catastrophic", "tier 1") are unaffected by this
    guard since they're unambiguous on their own.
    """
    classes = meta.get("classes", [])
    synonyms = meta.get("synonyms", {})
    cue_words = meta.get("numeric_cue_words")

    is_numeric_domain = classes and all(isinstance(c, (int, float)) and not isinstance(c, bool) for c in classes)
    allow_bare_numeric_match = not is_numeric_domain or not cue_words or any(
        has_word(w, query) for w in cue_words
    )

    if allow_bare_numeric_match:
        for cls in sorted(classes, key=lambda c: len(str(c)), reverse=True):
            if has_word(str(cls), query):
                return cls

    for syn in sorted(synonyms.keys(), key=len, reverse=True):
        if has_word(syn, query):
            return synonyms[syn]

    return None


# ==============================================================================
# Step 1: Agent Schema Selection (Schema-Only Context)
# ==============================================================================

def select_schema_for_task(query: str) -> dict[str, Any]:
    """
    Step 1: Inspects the query intent and selects the required table/view
    and columns from the schema without value-clutter.
    """
    selected_filter_cols = []

    # Check which columns are relevant for filtering
    for col, meta in COLUMN_DOMAINS.items():
        if has_word(col, query):
            selected_filter_cols.append(col)
            continue

        if match_domain_value(col, meta, query) is not None:
            selected_filter_cols.append(col)

    # Determine if aggregation is requested
    is_aggregation = any(
        has_word(term, query)
        for term in ["average", "avg", "mean", "count", "sum", "rate", "compare", "breakdown", "group by"]
    )

    # Determine projection columns
    if is_aggregation:
        projection_cols = ["COUNT(*) AS incident_count"]
        if any(has_word(t, query) for t in ["revenue", "financial", "loss"]):
            projection_cols.append("AVG(revenue_loss_usd) AS avg_revenue_loss")
        if any(has_word(t, query) for t in ["recovery", "days", "time"]):
            projection_cols.append("AVG(full_recovery_days) AS avg_recovery_days")
        if any(has_word(t, query) for t in ["impact", "downtime"]):
            projection_cols.append("AVG(production_impact_pct) AS avg_downtime_pct")
        if has_word("resilience", query):
            projection_cols.append("AVG(resilience_score) AS avg_resilience_score")
    else:
        projection_cols = [
            "disruption_id",
            "disruption_type",
            "industry",
            "supplier_tier",
            "supplier_region",
            "disruption_severity",
            "production_impact_pct",
            "revenue_loss_usd",
            "response_type",
            "full_recovery_days",
            "resilience_score",
            "prioritization_level",
            "top_risk_driver",
        ]

    return {
        "target_view": "v_disruption_details",
        "filter_columns": sorted(list(set(selected_filter_cols))),
        "projection_columns": projection_cols,
        "is_aggregation": is_aggregation,
    }


# ==============================================================================
# Step 2: Just-In-Time Value Injection
# ==============================================================================

# In-memory cache for dynamically fetched classes from Synapt Trident MCP
_SYNAPT_CLASSES_CACHE: dict[str, list] = {}


async def fetch_synapt_classes_for_columns(columns: list[str]) -> dict[str, list]:
    """
    Asynchronously queries Synapt Trident MCP knowledge graph for
    the controlled classes of the specified columns and caches them.
    """
    global _SYNAPT_CLASSES_CACHE
    try:
        async with SynaptService() as synapt:
            fetched = await synapt.get_column_classes(columns=columns, use_cache=True)
            _SYNAPT_CLASSES_CACHE.update(fetched)
            return fetched
    except Exception as e:
        # Fallback to already cached classes if any
        return {col: _SYNAPT_CLASSES_CACHE[col] for col in columns if col in _SYNAPT_CLASSES_CACHE}


def get_synapt_classes_sync(columns: list[str]) -> dict[str, list]:
    """
    Synchronous accessor to retrieve classes from Synapt Trident MCP cache,
    or queries the knowledge graph if the cache is cold.
    """
    global _SYNAPT_CLASSES_CACHE
    # If all requested columns are already in memory cache, return instantly (< 1ms)
    needed = [col for col in columns if col in COLUMN_DOMAINS and col not in _SYNAPT_CLASSES_CACHE]
    if not needed and _SYNAPT_CLASSES_CACHE:
        return {col: _SYNAPT_CLASSES_CACHE[col] for col in columns if col in _SYNAPT_CLASSES_CACHE}

    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(asyncio.run, fetch_synapt_classes_for_columns(columns)).result()
                return result
        else:
            return asyncio.run(fetch_synapt_classes_for_columns(columns))
    except Exception:
        return {}


def get_classes_for_columns(selected_columns: list[str], use_synapt: bool = True) -> dict[str, Any]:
    """
    Step 2: Fetches ground-truth classes and synonyms ONLY for the columns
    selected by Step 1. Dynamically pulls and grounds classes against the
    Synapt Trident MCP knowledge graph with in-memory caching and local fallback.
    """
    synapt_classes = {}
    if use_synapt:
        synapt_classes = get_synapt_classes_sync(selected_columns)

    injected_context = {}
    for col in selected_columns:
        if col in COLUMN_DOMAINS:
            # Prefer classes retrieved from Synapt Trident MCP if available
            classes = synapt_classes.get(col) or COLUMN_DOMAINS[col]["classes"]
            source = "synapt_trident_mcp" if col in synapt_classes else "local_ontology"

            injected_context[col] = {
                "classes": classes,
                "synonyms": COLUMN_DOMAINS[col].get("synonyms", {}),
                "numeric_cue_words": COLUMN_DOMAINS[col].get("numeric_cue_words"),
                "source": source,
            }
    return injected_context


# ==============================================================================
# Step 3: Entity Grounding & SQL Synthesis
# ==============================================================================

def synthesize_sql(
    query: str,
    schema_spec: dict[str, Any],
    injected_classes: dict[str, Any],
    limit: int = 50,
) -> str:
    """
    Step 3: Translates intent into grounded, parameterized MySQL query
    using the injected classes.
    """
    target_view = schema_spec.get("target_view", "v_disruption_details")
    is_aggregation = schema_spec.get("is_aggregation", False)

    # For aggregation/comparison queries ("X vs Y"), determine the GROUP BY
    # column FIRST so it can be excluded from WHERE filtering below — otherwise
    # a query like "Alternative Supplier vs Production Reroute" would get
    # filtered down to just the first-mentioned value instead of comparing
    # across all of them.
    group_col = None
    if is_aggregation:
        for col in ["response_type", "industry", "supplier_tier", "disruption_type", "supplier_region"]:
            if has_word(col, query) or any(has_word(syn, query) for syn in COLUMN_DOMAINS.get(col, {}).get("synonyms", {})):
                group_col = col
                break
        group_col = group_col or "response_type"

    where_clauses = []

    # Ground each injected filter column against query text
    for col, domain in injected_classes.items():
        if is_aggregation and col == group_col:
            continue

        matched_val = match_domain_value(col, domain, query)

        if matched_val is not None:
            if isinstance(matched_val, bool):
                where_clauses.append(f"{col} = {str(matched_val).upper()}")
            elif isinstance(matched_val, str):
                where_clauses.append(f"{col} = '{matched_val}'")
            elif isinstance(matched_val, (int, float)):
                if col == "disruption_severity" and (has_word("severe", query) or has_word("high", query)):
                    where_clauses.append(f"{col} >= 4")
                else:
                    where_clauses.append(f"{col} = {matched_val}")

    # Build SQL string
    if is_aggregation:
        select_part = f"{group_col}, " + ", ".join(schema_spec["projection_columns"])
        where_part = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql = f"SELECT {select_part} FROM {target_view} {where_part} GROUP BY {group_col} ORDER BY incident_count DESC LIMIT {limit};"
    else:
        select_part = ", ".join(schema_spec["projection_columns"])
        where_part = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Determine sensible ORDER BY
        order_by = "revenue_loss_usd DESC"
        if has_word("recovery", query):
            order_by = "full_recovery_days ASC"
        elif has_word("severity", query):
            order_by = "disruption_severity DESC"

        sql = f"SELECT {select_part} FROM {target_view} {where_part} ORDER BY {order_by} LIMIT {limit};"

    # Clean double spaces
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql


def synthesize_sql_with_gemini(
    query: str,
    schema_spec: dict[str, Any],
    injected_classes: dict[str, Any],
    limit: int = 50,
) -> tuple[str, str]:
    """
    Synthesizes grounded SQL using Google Gemini API (gemini-2.0-flash / gemini-2.0-flash-lite).
    Passes schema and Synapt-retrieved classes to generate safe, optimized queries.
    Gracefully falls back to deterministic synthesize_sql() on failure or missing key.
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        return synthesize_sql(query, schema_spec, injected_classes, limit=limit), "deterministic_sql_builder"

    try:
        from google import genai

        client = genai.Client(api_key=gemini_key)

        classes_summary = {}
        for col, meta in injected_classes.items():
            classes_summary[col] = meta.get("classes", [])

        prompt = f"""You are an expert MySQL SQL Developer for a supply chain crisis management system.
Given the user request, the database schema for the unified view `v_disruption_details`, and the controlled classes retrieved from Synapt, generate a valid read-only MySQL SELECT query.

User Query: "{query}"

Target View: `v_disruption_details`
Available Columns:
disruption_id, disruption_type, industry, supplier_tier, supplier_region, supplier_size,
has_backup_supplier, disruption_severity, production_impact_pct, revenue_loss_usd,
response_type, response_time_days, partial_recovery_days, full_recovery_days,
permanent_supplier_change, resilience_score, prioritization_level, top_risk_driver, recommended_strategy

Synapt Grounding Classes:
{json.dumps(classes_summary, indent=2)}

Rules:
1. ONLY query `v_disruption_details`. Never query any other table or view.
2. Generate ONLY a single SELECT query. Never use DROP, DELETE, INSERT, UPDATE, ALTER.
3. For categorical filters, match the values against the controlled classes exactly.
4. Support aggregations (COUNT, AVG, SUM, GROUP BY) if asked for summary/averages, otherwise SELECT disruption_id, disruption_type, industry, supplier_tier, supplier_region, disruption_severity, production_impact_pct, revenue_loss_usd, response_type, full_recovery_days, resilience_score.
5. Include an appropriate ORDER BY (e.g. revenue_loss_usd DESC) and LIMIT {limit}.
6. Output ONLY the raw SQL query with no explanation, no backticks, and no markdown formatting.
"""

        for model_name in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                raw_text = response.text.strip() if response and response.text else ""
                raw_text = re.sub(r"^```(?:sql)?\s*", "", raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r"\s*```$", "", raw_text).strip()

                if raw_text.upper().startswith("SELECT"):
                    valid = validate_sql_query(raw_text)
                    return valid, f"gemini_sql_builder ({model_name})"
            except Exception:
                continue

    except Exception:
        pass

    return synthesize_sql(query, schema_spec, injected_classes, limit=limit), "deterministic_sql_builder"


# ==============================================================================
# Step 4: Safety Guardrails Validator
# ==============================================================================

def validate_sql_query(sql: str) -> str:
    """
    Step 4: Strict validation ensuring the query is read-only, targets
    whitelisted tables, and includes a safe limit.
    """
    cleaned = sql.strip().rstrip(";")
    tokens = re.split(r"\s+", cleaned)
    if not tokens:
        raise SQLSecurityException("Empty query generated.")

    first_keyword = tokens[0].upper()
    if first_keyword != "SELECT":
        raise SQLSecurityException(
            f"Security Violation: Query must begin with SELECT (received '{first_keyword}')."
        )

    # Check for forbidden destructive keywords
    upper_sql = cleaned.upper()
    for forbidden in FORBIDDEN_SQL_KEYWORDS:
        # Match whole word
        if re.search(rf"\b{forbidden}\b", upper_sql):
            raise SQLSecurityException(
                f"Security Violation: Forbidden keyword '{forbidden}' detected in SQL query."
            )

    # Check for comment injection (-- or /* */)
    if "--" in cleaned or "/*" in cleaned:
        raise SQLSecurityException("Security Violation: Comment sequences are disallowed in generated SQL.")

    # Table whitelist validation
    table_match = re.search(r"\bFROM\s+([a-zA-Z0-9_]+)", upper_sql)
    if not table_match:
        raise SQLSecurityException("Query does not specify a valid FROM clause.")
    target_table = table_match.group(1).lower()
    if target_table not in ALLOWED_TABLES:
        raise SQLSecurityException(
            f"Security Violation: Table '{target_table}' is not in the allowed schema whitelist."
        )

    # Ensure LIMIT clause exists
    if "LIMIT" not in upper_sql:
        cleaned += " LIMIT 50"

    return cleaned + ";"


# ==============================================================================
# Step 5: End-to-End Orchestrator & Execution
# ==============================================================================

def build_and_execute_sql(query: str, limit: int = 50, use_synapt: bool = True) -> dict[str, Any]:
    """
    Full pipeline:
      1. Schema selection (Agent)
      2. Just-in-time value injection from Synapt Trident MCP knowledge graph
      3. Synthesis
      4. Guardrail validation
      5. MySQL Execution
    """
    start_time = time.time()

    # 1. Schema Selection
    schema_spec = select_schema_for_task(query)

    # 2. Just-In-Time Value Injection (via Synapt Trident MCP)
    injected_classes = get_classes_for_columns(schema_spec["filter_columns"], use_synapt=use_synapt)

    # 3. SQL Synthesis (Gemini LLM grounded with Synapt classes, fallback to deterministic)
    raw_sql, sql_engine_used = synthesize_sql_with_gemini(query, schema_spec, injected_classes, limit=limit)

    # 4. Guardrail Validation
    validated_sql = validate_sql_query(raw_sql)

    # 5. Database Execution
    with engine.connect() as conn:
        result = conn.execute(text(validated_sql))
        rows = [dict(row._mapping) for row in result]
        columns = list(result.keys()) if rows else []

    elapsed_ms = (time.time() - start_time) * 1000

    classes_source = (
        "synapt_trident_mcp"
        if any(c.get("source") == "synapt_trident_mcp" for c in injected_classes.values())
        else "local_ontology"
    )

    return {
        "user_query": query,
        "selected_filter_columns": schema_spec["filter_columns"],
        "injected_classes_count": len(injected_classes),
        "classes_source": classes_source,
        "generated_sql": validated_sql,
        "sql_engine": sql_engine_used,
        "row_count": len(rows),
        "columns": columns,
        "records": rows,
        "execution_time_ms": round(elapsed_ms, 2),
    }


async def build_and_execute_sql_async(
    query: str, limit: int = 50, use_synapt: bool = True
) -> dict[str, Any]:
    """
    Asynchronous version of build_and_execute_sql leveraging native async
    SynaptService calls for FastAPI endpoints and multi-agent workflows.
    """
    start_time = time.time()
    schema_spec = select_schema_for_task(query)

    synapt_classes = {}
    if use_synapt:
        synapt_classes = await fetch_synapt_classes_for_columns(schema_spec["filter_columns"])

    injected_classes = {}
    for col in schema_spec["filter_columns"]:
        if col in COLUMN_DOMAINS:
            classes = synapt_classes.get(col) or COLUMN_DOMAINS[col]["classes"]
            source = "synapt_trident_mcp" if col in synapt_classes else "local_ontology"
            injected_classes[col] = {
                "classes": classes,
                "synonyms": COLUMN_DOMAINS[col].get("synonyms", {}),
                "numeric_cue_words": COLUMN_DOMAINS[col].get("numeric_cue_words"),
                "source": source,
            }

    raw_sql, sql_engine_used = synthesize_sql_with_gemini(query, schema_spec, injected_classes, limit=limit)
    validated_sql = validate_sql_query(raw_sql)

    with engine.connect() as conn:
        result = conn.execute(text(validated_sql))
        rows = [dict(row._mapping) for row in result]
        columns = list(result.keys()) if rows else []

    elapsed_ms = (time.time() - start_time) * 1000

    classes_source = (
        "synapt_trident_mcp"
        if any(c.get("source") == "synapt_trident_mcp" for c in injected_classes.values())
        else "local_ontology"
    )

    return {
        "user_query": query,
        "selected_filter_columns": schema_spec["filter_columns"],
        "injected_classes_count": len(injected_classes),
        "classes_source": classes_source,
        "generated_sql": validated_sql,
        "sql_engine": sql_engine_used,
        "row_count": len(rows),
        "columns": columns,
        "records": rows,
        "execution_time_ms": round(elapsed_ms, 2),
    }


# ==============================================================================
# CLI Self-Test
# ==============================================================================

if __name__ == "__main__":
    print("=== Testing Synapt SQL Builder ===")
    test_queries = [
        "Find severe ransomware incidents affecting chip makers in APAC",
        "Show me factory fire disruptions in Automotive without backup supplier",
        "What is the average financial loss and recovery time when companies use Alternative Supplier vs Production Reroute?",
        "Find top 5 catastrophic natural disaster disruptions in Europe ordered by revenue loss",
    ]

    for q in test_queries:
        print(f"\n[QUERY]: {q}")
        res = build_and_execute_sql(q, limit=3)
        print(f"[SQL]: {res['generated_sql']}")
        print(f"[RESULTS]: {res['row_count']} rows returned in {res['execution_time_ms']} ms")
        if res["records"]:
            print(f"Sample row: {res['records'][0]}")
