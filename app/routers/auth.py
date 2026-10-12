"""
FastAPI Router for Authentication & JWT endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

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

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/login",
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


@router.post(
    "/token",
    response_model=TokenResponse,
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
                headers={"WWW-Authenticate": "Bearer"},
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


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Authenticated User Profile",
)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user details from the separate auth.db."""
    return current_user
