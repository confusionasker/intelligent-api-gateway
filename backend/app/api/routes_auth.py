"""Authentication and API Key management routes."""

import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    ApiKeyCreateRequest,
    ApiKeyResponse,
)
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Authentication & Keys"])


# ---------------------------------------------------------
# User Authentication Endpoints
# ---------------------------------------------------------

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account with secure bcrypt password hashing."""
    existing_user = db.query(User).filter(User.username == payload.username.strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = User(
        username=payload.username.strip(),
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Registered new user: {user.username}")
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate credentials and issue a signed JWT access token."""
    user = db.query(User).filter(User.username == payload.username.strip()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    token = create_access_token(data={"sub": user.username, "user_id": user.id})
    logger.info(f"User {user.username} successfully logged in.")
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Return identity and status of currently authenticated user."""
    return current_user


# ---------------------------------------------------------
# API Key Management Endpoints
# ---------------------------------------------------------

@router.post("/keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a cryptographically secure API key for the authenticated user."""
    raw_key = f"pg_live_{secrets.token_hex(16)}"

    api_key_record = ApiKey(
        key=raw_key,
        name=payload.name or "Primary Key",
        user_id=current_user.id,
        rate_limit=payload.rate_limit or 20,
        is_active=True,
    )
    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)
    logger.info(f"Generated API key {api_key_record.id} for user {current_user.username}")
    return api_key_record


@router.get("/keys", response_model=List[ApiKeyResponse])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all API keys belonging to the authenticated user."""
    return db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()


@router.delete("/keys/{key_id}", status_code=status.HTTP_200_OK)
def deactivate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deactivate an API key."""
    key_record = (
        db.query(ApiKey)
        .filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
        .first()
    )
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    key_record.is_active = False
    db.commit()
    logger.info(f"Deactivated API key {key_id}")
    return {"message": f"API key {key_id} deactivated successfully"}
