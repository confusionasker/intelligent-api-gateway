"""Gateway forwarding service that proxies client requests to downstream targets.

Validates destination URLs against allowlists, enforces timeouts, measures latency,
and delegates metrics logging.
"""

import time
from urllib.parse import urlparse
from typing import Any, Dict, Optional, Tuple
import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.api_key import ApiKey
from app.services.metrics_service import MetricsService
from app.utils.logger import logger


class GatewayService:
    @staticmethod
    def validate_target_url(target_url: str) -> None:
        """Validate destination URL scheme and ensure the hostname is in the security allowlist."""
        parsed = urlparse(target_url)
        if parsed.scheme not in ("http", "https"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported URL scheme '{parsed.scheme}'. Only http and https are allowed.",
            )

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid target URL: missing hostname.",
            )

        # Allow wildcard '*' or configured hosts
        allowed = settings.allowed_hosts_list
        if "*" not in allowed and hostname not in allowed and not any(hostname.endswith(f".{h}") for h in allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Target host '{hostname}' is not in the gateway security allowlist.",
            )

    @classmethod
    async def forward_request(
        cls,
        db: Session,
        api_key: ApiKey,
        target_url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, float, Any, Dict[str, str]]:
        """Forward an HTTP request to downstream service, calculate latency, and record metrics."""
        cls.validate_target_url(target_url)
        parsed = urlparse(target_url)
        endpoint_path = parsed.path or "/"

        # Prepare forwarded headers (excluding hop-by-hop headers)
        forward_headers = {k: v for k, v in (headers or {}).items() if k.lower() not in ("host", "content-length")}
        forward_headers["X-Forwarded-By"] = "PulseGate-Gateway"
        forward_headers["X-Consumer-Key-Id"] = str(api_key.id)

        start_time = time.perf_counter()
        status_code = 502
        response_data: Any = None
        response_headers: Dict[str, str] = {}
        is_error = False

        timeout = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=target_url,
                    headers=forward_headers,
                    json=body if isinstance(body, (dict, list)) else None,
                    content=body if isinstance(body, (str, bytes)) else None,
                    params=params,
                )
                status_code = response.status_code
                is_error = status_code >= 400
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text

                # Capture downstream content-type if present
                for h in ("content-type", "x-request-id"):
                    if h in response.headers:
                        response_headers[h] = response.headers[h]

            except httpx.TimeoutException as exc:
                logger.error(f"Downstream timeout connecting to {target_url}: {exc}")
                status_code = status.HTTP_504_GATEWAY_TIMEOUT
                response_data = {"detail": "Downstream service timeout"}
                is_error = True
            except httpx.RequestError as exc:
                logger.error(f"Downstream connection error for {target_url}: {exc}")
                status_code = status.HTTP_502_BAD_GATEWAY
                response_data = {"detail": f"Downstream service unavailable: {str(exc)}"}
                is_error = True

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Record metrics in SQLite database
        MetricsService.record_request(
            db=db,
            endpoint=endpoint_path,
            method=method.upper(),
            status_code=status_code,
            latency_ms=latency_ms,
            api_key_id=api_key.id,
            is_error=is_error,
        )

        return status_code, latency_ms, response_data, response_headers
