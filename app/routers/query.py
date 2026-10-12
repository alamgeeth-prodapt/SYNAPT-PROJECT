"""
FastAPI Router for Natural Language SQL Generation and Synapt Knowledge Graph.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import User, get_current_user
from app.services.sql_builder import build_and_execute_sql_async
from app.services.synapt_service import SynaptService

router = APIRouter(tags=["Natural Language SQL Builder & Synapt"])


class SQLQueryRequest(BaseModel):
    query: str = Field(
        ...,
        json_schema_extra={"example": "Find severe ransomware incidents affecting chip makers in APAC"},
        description="Natural language query to be translated into grounded SQL on v_disruption_details",
    )
    limit: int = Field(default=50, ge=1, le=500, description="Maximum number of rows to return")


class SQLQueryResponse(BaseModel):
    user_query: str
    selected_filter_columns: list[str]
    injected_classes_count: int
    classes_source: str
    generated_sql: str
    row_count: int
    columns: list[str]
    records: list[dict[str, Any]]
    execution_time_ms: float


@router.post(
    "/api/v1/query-sql",
    response_model=SQLQueryResponse,
    summary="Graph-Guided Natural Language to SQL Execution (JWT Protected)",
)
async def execute_natural_language_query(
    req: SQLQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Translates user questions into grounded read-only MySQL queries:
    1. Schema Pruning (picks required columns).
    2. Synapt Trident MCP dynamic class injection.
    3. Safe SQL synthesis targeting `v_disruption_details`.
    4. Guardrail security validation & execution.
    """
    try:
        res = await build_and_execute_sql_async(req.query, limit=req.limit, use_synapt=True)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SQL synthesis/execution error: {str(e)}",
        )


@router.get(
    "/api/v1/schema/ontology",
    tags=["Synapt Knowledge Graph"],
    summary="Fetch Controlled Classes from Synapt Trident MCP",
)
async def get_schema_ontology():
    """Retrieves ground-truth controlled categories directly from the Synapt Trident MCP Knowledge Graph."""
    try:
        async with SynaptService() as syn:
            classes = await syn.get_column_classes(use_cache=True)
            stats = await syn.get_stats()
            return {
                "source": "synapt_trident_mcp",
                "knowledge_graph_stats": stats,
                "controlled_classes": classes,
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ontology from Synapt: {str(e)}",
        )
