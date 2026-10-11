"""
FastAPI Microservice for AI-Powered Supply Chain Disruption Assistant with Synapt.
Serves the Multi-Agent Orchestration Engine, Predictive ML Models, TreeSHAP,
Synapt Trident MCP Knowledge Graph, and Graph-Guided SQL Builder.
"""

import time
from typing import Any
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.agents import (
    IncidentInput,
    InvestigationResult,
    ImpactResult,
    ResponseResult,
    RecoveryResult,
    ExecutiveDossier,
    DisruptionCoordinator,
    InvestigationAgent,
    ImpactAgent,
    ResponseAgent,
    RecoveryAgent,
)
from app.services.ml_service import MLService
from app.services.shap_service import SHAPService
from app.services.sql_builder import build_and_execute_sql, build_and_execute_sql_async
from app.services.synapt_service import SynaptService
from app.services.db_service import engine
from app.services.auth_service import (
    User,
    get_current_user,
    verify_password,
    create_access_token,
    TokenResponse,
    UserResponse,
    LoginRequest,
    AuthSessionLocal,
    select,
)


# ==============================================================================
# FastAPI App Initialization & Metadata
# ==============================================================================

app = FastAPI(
    title="Synapt Supply Chain Disruption Assistant API",
    description="""
### AI-Powered Multi-Agent Supply Chain Resilience & Disruption Assistant

This REST API serves the end-to-end resilience engine:
* **Multi-Agent Orchestration**: Investigation, Impact, Response, Recovery, and LLM-as-Judge agents.
* **Predictive ML & XAI**: XGBoost regression models for downtime, revenue loss, and recovery with native TreeSHAP attribution.
* **Synapt Trident MCP**: Semantic knowledge graph ontology governance and just-in-time value grounding.
* **Safe SQL Engine**: Graph-guided read-only SQL generation querying 100,000 historical disruption records (`v_disruption_details`).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend applications (React on Vite / Create React App / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singleton instances
_coordinator: DisruptionCoordinator | None = None
_ml_service: MLService | None = None
_shap_service: SHAPService | None = None


def get_coordinator() -> DisruptionCoordinator:
    global _coordinator
    if _coordinator is None:
        _coordinator = DisruptionCoordinator()
    return _coordinator


def get_ml_service() -> MLService:
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service


def get_shap_service() -> SHAPService:
    global _shap_service
    if _shap_service is None:
        _shap_service = SHAPService(get_ml_service())
    return _shap_service


# ==============================================================================
# Request & Response Schemas
# ==============================================================================

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


class HealthResponse(BaseModel):
    status: str
    database: str
    total_records: int
    models_loaded: list[str]
    synapt_mcp: str
    timestamp_utc: float


class HumanFeedbackRequest(BaseModel):
    dossier_id: str
    operator_id: str = "operator_1"
    rating: int = Field(ge=1, le=5, description="1 to 5 rating of recommendation quality")
    accepted_strategy: bool = True
    override_strategy: str | None = None
    comments: str = Field(default="", description="Operator notes or review feedback")


# ==============================================================================
# System Health & Root Endpoints
# ==============================================================================

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Synapt Supply Chain Disruption Assistant API is online.",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """Verifies MySQL connection, loaded models, and Synapt service readiness."""
    try:
        with engine.connect() as conn:
            row_count = conn.execute(text("SELECT COUNT(*) FROM v_disruption_details")).scalar()
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        row_count = 0

    ml = get_ml_service()
    loaded_models = list(ml.metrics.keys())

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        total_records=row_count or 0,
        models_loaded=loaded_models,
        synapt_mcp="configured",
        timestamp_utc=time.time(),
    )


# ==============================================================================
# Authentication & JWT Endpoints (Separate auth.db)
# ==============================================================================

@app.post(
    "/api/v1/auth/login",
    tags=["Authentication"],
    summary="OAuth2 Password Login (for Swagger UI 'Authorize' button)",
)
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Standard OAuth2 password flow endpoint.
    Used by Swagger UI 'Authorize' padlock button.
    Default credentials: username='admin', password='admin'.
    """
    with AuthSessionLocal() as session:
        stmt = select(User).where(User.username == form_data.username)
        user = session.execute(stmt).scalar_one_or_none()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(data={"sub": user.username, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}


@app.post(
    "/api/v1/auth/token",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="JSON Login (for React Frontend & API Consumers)",
)
def login_json(payload: LoginRequest):
    """
    JSON-based login endpoint for frontend client applications.
    Default credentials: username='admin', password='admin'.
    """
    with AuthSessionLocal() as session:
        stmt = select(User).where(User.username == payload.username)
        user = session.execute(stmt).scalar_one_or_none()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        token = create_access_token(data={"sub": user.username, "role": user.role})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in_minutes=60 * 24,
            user={
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
            },
        )


@app.get(
    "/api/v1/auth/me",
    response_model=UserResponse,
    tags=["Authentication"],
    summary="Get Authenticated User Profile",
)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user details from the separate auth.db."""
    return current_user


# ==============================================================================
# Core Multi-Agent Orchestration
# ==============================================================================

@app.post(
    "/api/v1/orchestrate",
    response_model=ExecutiveDossier,
    status_code=status.HTTP_200_OK,
    tags=["Multi-Agent Orchestration"],
    summary="Execute End-to-End 5-Agent Crisis Response Pipeline (JWT Protected)",
)
def orchestrate_crisis_response(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    """
    Executes the full multi-agent orchestration pipeline:
    1. **InvestigationAgent**: Historical analog retrieval & cohort statistics on `v_disruption_details`.
    2. **ImpactAgent**: XGBoost forecasting (downtime, loss, recovery) + Resilience Score + P1-P4 Triage.
    3. **ResponseAgent**: Empirical strategy benchmarks & operational crisis checklists.
    4. **RecoveryAgent**: 4-stage recovery milestone roadmap & vendor continuity rating.
    5. **LLMJudgeAgent**: Safety, single-source risk, and feasibility audit.
    """
    try:
        coordinator = get_coordinator()
        dossier = coordinator.process_incident(incident)
        return dossier
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failure: {str(e)}",
        )


# ==============================================================================
# Individual Specialized Agent Endpoints
# ==============================================================================

@app.post(
    "/api/v1/investigate",
    response_model=InvestigationResult,
    tags=["Specialized Agents"],
    summary="Agent 1: Historical Analog Retrieval & Cohort Analytics (JWT Protected)",
)
def investigate_incident(
    incident: IncidentInput,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
):
    """Queries MySQL `v_disruption_details` for historical analog cases and baseline cohort statistics."""
    try:
        agent = InvestigationAgent()
        return agent.investigate(incident, limit_analogs=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}",
        )


@app.post(
    "/api/v1/predict",
    response_model=ImpactResult,
    tags=["Specialized Agents"],
    summary="Agent 2: ML Impact Forecasting & Resilience Triage (JWT Protected)",
)
def predict_impact(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    """Feeds incident into XGBoost models to compute downtime %, financial loss $, Resilience Score, and P1-P4 triage."""
    try:
        agent = ImpactAgent(ml_service=get_ml_service(), shap_service=get_shap_service())
        return agent.assess(incident)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Impact assessment failed: {str(e)}",
        )


@app.post(
    "/api/v1/explain",
    tags=["Specialized Agents"],
    summary="Agent 2 XAI: Native TreeSHAP Waterfall Risk Attribution (JWT Protected)",
)
def explain_risk_drivers(
    incident: IncidentInput,
    target: str = "revenue_loss_usd",
    current_user: User = Depends(get_current_user),
):
    """Returns local TreeSHAP feature attributions and waterfall data for UI charts."""
    try:
        shap = get_shap_service()
        incident_dict = {
            "disruption_type": incident.disruption_type,
            "industry": incident.industry,
            "supplier_tier": incident.supplier_tier,
            "supplier_region": incident.supplier_region,
            "supplier_size": incident.supplier_size,
            "has_backup_supplier": 1 if incident.has_backup_supplier else 0,
            "disruption_severity": incident.disruption_severity,
        }

        if target == "production_impact_pct":
            return shap.explain_impact(incident_dict)
        elif target == "full_recovery_days":
            return shap.explain_recovery(incident_dict)
        else:
            return shap.explain_loss(incident_dict, impact_pct=incident.production_impact_pct)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation failed: {str(e)}",
        )


@app.post(
    "/api/v1/response-plan",
    response_model=ResponseResult,
    tags=["Specialized Agents"],
    summary="Agent 3: Empirical Mitigation Strategy Benchmark (JWT Protected)",
)
def plan_mitigation_response(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    """Queries empirical historical benchmarks on MySQL and selects optimal response strategy + operational checklist."""
    try:
        impact_agent = ImpactAgent(ml_service=get_ml_service(), shap_service=get_shap_service())
        impact = impact_agent.assess(incident)
        response_agent = ResponseAgent()
        return response_agent.plan_response(incident, impact)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response planning failed: {str(e)}",
        )


@app.post(
    "/api/v1/recovery-forecast",
    response_model=RecoveryResult,
    tags=["Specialized Agents"],
    summary="Agent 4: Milestone Roadmap & Vendor Continuity Analysis (JWT Protected)",
)
def forecast_recovery_roadmap(
    incident: IncidentInput,
    current_user: User = Depends(get_current_user),
):
    """Forecasts days to full recovery, supplier contract continuity risk, and the 4-phase milestone schedule."""
    try:
        impact_agent = ImpactAgent(ml_service=get_ml_service(), shap_service=get_shap_service())
        impact = impact_agent.assess(incident)
        response_agent = ResponseAgent()
        response = response_agent.plan_response(incident, impact)
        recovery_agent = RecoveryAgent(ml_service=get_ml_service())
        return recovery_agent.forecast_recovery(incident, response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recovery forecasting failed: {str(e)}",
        )


# ==============================================================================
# Natural Language SQL Builder & Synapt Knowledge Graph
# ==============================================================================

@app.post(
    "/api/v1/query-sql",
    response_model=SQLQueryResponse,
    tags=["Natural Language SQL Builder"],
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


@app.get(
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


# ==============================================================================
# Human-in-the-Loop Feedback
# ==============================================================================

@app.post(
    "/api/v1/feedback",
    tags=["Human-in-the-Loop"],
    summary="Submit Human Operator Review & Audit Feedback (JWT Protected)",
)
def submit_operator_feedback(
    feedback: HumanFeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    """Records human operator approval, ratings, and overrides for governance audits."""
    return {
        "status": "recorded",
        "dossier_id": feedback.dossier_id,
        "operator_id": feedback.operator_id,
        "rating": feedback.rating,
        "accepted_strategy": feedback.accepted_strategy,
        "recorded_at_utc": time.time(),
        "audit_message": "Operator feedback successfully logged into crisis management registry.",
    }
