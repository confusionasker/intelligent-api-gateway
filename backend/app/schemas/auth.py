"""Pydantic schemas for authentication and API key management."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreateRequest(BaseModel):
    name: Optional[str] = "Primary Key"
    rate_limit: Optional[int] = Field(default=20, ge=1, le=10000)


class ApiKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    rate_limit: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
