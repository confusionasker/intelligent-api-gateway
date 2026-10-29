"""API Gateway forwarding routes and downstream demo targets."""

import asyncio
from typing import Any
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.api_key import ApiKey
from app.schemas.gateway import GatewayRequest, GatewayResponse
from app.core.dependencies import get_valid_api_key
from app.services.rate_limiter import rate_limiter
from app.services.gateway_service import GatewayService
from app.services.metrics_service import MetricsService
from app.utils.logger import logger

router = APIRouter(tags=["API Gateway"])


# ---------------------------------------------------------
# Demo Target Endpoints (Built-in Downstream Service)
# ---------------------------------------------------------

@router.get("/demo/hello")
def demo_hello():
    """Standard downstream demo endpoint returning greeting."""
    return {"message": "Hello from downstream service"}


@router.get("/demo/slow")
async def demo_slow():
    """Downstream endpoint with artificial latency to simulate slow dependencies."""
    await asyncio.sleep(0.45)
    return {"message": "Delayed response from downstream service", "delayed_ms": 450}


@router.get("/demo/error")
def demo_error():
    """Downstream endpoint returning 500 error to simulate service failures."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Downstream database connection failure simulation",
    )


# ---------------------------------------------------------
# Gateway Forwarding Endpoint
# ---------------------------------------------------------

@router.post("/api/gateway/request", response_model=GatewayResponse)
async def gateway_forward_request(
    payload: GatewayRequest,
    api_key: ApiKey = Depends(get_valid_api_key),
    db: Session = Depends(get_db),
):
    """Secure Gateway Request Forwarding.
    
    1. Authenticates client via X-API-Key.
    2. Enforces Token Bucket rate limiting in Redis.
    3. Forwards request asynchronously to downstream target.
    4. Measures response latency.
    5. Saves metrics to SQLite.
    6. Returns downstream response with RateLimit headers.
    """
    # Check Token Bucket rate limit
    limit_result = rate_limiter.check_rate_limit(
        key=api_key.key,
        capacity=api_key.rate_limit,
    )

    if not limit_result.allowed:
        logger.warning(
            f"Rate limit exceeded for key {api_key.key[:10]}... Retry after {limit_result.retry_after}s"
        )
        try:
            parsed = urlparse(payload.target_url)
            endpoint_path = parsed.path or "/"
        except Exception:
            endpoint_path = "/unknown"

        # Record 429 Rate Limit error into metrics database
        MetricsService.record_request(
            db=db,
            endpoint=endpoint_path,
            method=payload.method,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            latency_ms=1.5,
            api_key_id=api_key.id,
            is_error=True,
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": limit_result.retry_after,
            },
            headers={
                **limit_result.get_headers(),
                "Retry-After": str(limit_result.retry_after),
            },
        )

    # Forward downstream request
    status_code, latency_ms, data, headers = await GatewayService.forward_request(
        db=db,
        api_key=api_key,
        target_url=payload.target_url,
        method=payload.method,
        headers=payload.headers,
        body=payload.body,
        params=payload.params,
    )

    combined_headers = {
        **headers,
        **limit_result.get_headers(),
    }

    return JSONResponse(
        status_code=status_code if status_code < 400 else status_code,
        content={
            "status_code": status_code,
            "latency_ms": latency_ms,
            "data": data,
            "headers": headers,
        },
        headers=combined_headers,
    )
