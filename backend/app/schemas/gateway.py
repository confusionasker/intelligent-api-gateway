"""Pydantic schemas for API Gateway forwarding."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class GatewayRequest(BaseModel):
    target_url: str = Field(..., description="Target downstream service URL (must be allowlisted)")
    method: str = Field(default="GET", description="HTTP method e.g. GET, POST, PUT, DELETE")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Optional forwarded headers")
    body: Optional[Any] = Field(default=None, description="Optional request payload")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Optional query parameters")


class GatewayResponse(BaseModel):
    status_code: int
    latency_ms: float
    data: Any
    headers: Dict[str, str] = Field(default_factory=dict)
