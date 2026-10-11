"""
Authentication & JWT Service.
Uses an isolated, separate database (`auth.db`) completely detached from the MySQL analytical database.
Seeds default user 'admin' with password 'admin' on startup.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ==============================================================================
# Configuration & Isolated Auth Database
# ==============================================================================

AUTH_DB_PATH = os.getenv("AUTH_DB_PATH", "D:/SYNAPT-PROJECT/auth.db")
AUTH_DATABASE_URL = f"sqlite:///{AUTH_DB_PATH}"

# Minimum 32-byte secret key for RFC 7518 SHA256 compliance
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "synapt_super_secure_enterprise_jwt_secret_key_supply_chain_2026_x99",
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

auth_engine = create_engine(
    AUTH_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
AuthSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)


class BaseAuth(DeclarativeBase):
    pass


class User(BaseAuth):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# OAuth2 scheme for Swagger UI "Authorize" lock button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ==============================================================================
# Pydantic Schemas
# ==============================================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: dict[str, Any]


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    username: str = "admin"
    password: str = "admin"


# ==============================================================================
# Password Hashing & JWT Helpers
# ==============================================================================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==============================================================================
# Database Initialization & Seeding ('admin' / 'admin')
# ==============================================================================

def init_auth_db():
    """Initializes the separate auth.db SQLite schema and seeds admin user."""
    BaseAuth.metadata.create_all(bind=auth_engine)

    with AuthSessionLocal() as session:
        stmt = select(User).where(User.username == "admin")
        existing_admin = session.execute(stmt).scalar_one_or_none()

        if not existing_admin:
            admin_user = User(
                username="admin",
                hashed_password=hash_password("admin"),
                role="admin",
                is_active=True,
            )
            session.add(admin_user)
            session.commit()
            print("[Auth] Created default user 'admin' with password 'admin' in separate auth.db")


# ==============================================================================
# Dependency: Get Current Authenticated User
# ==============================================================================

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    with AuthSessionLocal() as session:
        stmt = select(User).where(User.username == username)
        user = session.execute(stmt).scalar_one_or_none()
        if user is None or not user.is_active:
            raise credentials_exception
        return user


# Run initial setup on module load
init_auth_db()
