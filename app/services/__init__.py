"""
Services package: Synapt integration, Safe SQL builder, ML inference, and SHAP attribution.
Also provides backward-compatible re-exports for core database and security utilities.
"""

from app.core.database import (
    engine,
    SessionLocal,
    get_session,
    test_connection,
    fetch_disruption_details,
)
from app.core.security import (
    User,
    get_current_user,
    verify_password,
    create_access_token,
    TokenResponse,
    UserResponse,
    LoginRequest,
    AuthSessionLocal,
)
from app.services.synapt_service import SynaptService
from app.services.ml_service import MLService
from app.services.shap_service import SHAPService
from app.services.sql_builder import build_and_execute_sql, build_and_execute_sql_async

__all__ = [
    "engine",
    "SessionLocal",
    "get_session",
    "test_connection",
    "fetch_disruption_details",
    "User",
    "get_current_user",
    "verify_password",
    "create_access_token",
    "TokenResponse",
    "UserResponse",
    "LoginRequest",
    "AuthSessionLocal",
    "SynaptService",
    "MLService",
    "SHAPService",
    "build_and_execute_sql",
    "build_and_execute_sql_async",
]
