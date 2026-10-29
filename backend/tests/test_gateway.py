"""Tests for API Gateway request forwarding, security validation, and demo endpoints."""

from unittest.mock import patch
import httpx
from app.models.api_key import ApiKey
from app.services.rate_limiter import _in_memory_buckets, get_redis_client


def test_demo_hello_endpoint(client):
    resp = client.get("/demo/hello")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello from downstream service"


def test_demo_slow_endpoint(client):
    resp = client.get("/demo/slow")
    assert resp.status_code == 200
    assert "delayed_ms" in resp.json()


def test_demo_error_endpoint(client):
    resp = client.get("/demo/error")
    assert resp.status_code == 500


def test_gateway_missing_api_key(client):
    resp = client.post(
        "/api/gateway/request",
        json={"target_url": "http://localhost:8000/demo/hello", "method": "GET"},
    )
    assert resp.status_code == 401
    assert "Missing X-API-Key" in resp.json()["error"]["message"]


def test_gateway_invalid_api_key(client):
    resp = client.post(
        "/api/gateway/request",
        json={"target_url": "http://localhost:8000/demo/hello", "method": "GET"},
        headers={"X-API-Key": "invalid_fake_key_9999"},
    )
    assert resp.status_code == 401
    assert "Invalid or deactivated" in resp.json()["error"]["message"]


def test_gateway_rejects_unallowed_host(client):
    resp = client.post(
        "/api/gateway/request",
        json={"target_url": "http://malicious-external-target.com/steal", "method": "GET"},
        headers={"X-API-Key": "pg_live_test_api_key_12345"},
    )
    assert resp.status_code == 403
    assert "not in the gateway security allowlist" in resp.json()["error"]["message"]


@patch("httpx.AsyncClient.request")
def test_gateway_forward_valid_request(mock_request, client):
    # Mock downstream service response
    mock_request.return_value = httpx.Response(
        status_code=200,
        json={"message": "Hello from downstream service"},
        headers={"content-type": "application/json"},
    )

    resp = client.post(
        "/api/gateway/request",
        json={"target_url": "http://localhost:8000/demo/hello", "method": "GET"},
        headers={"X-API-Key": "pg_live_test_api_key_12345"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status_code"] == 200
    assert "latency_ms" in data
    assert "X-RateLimit-Limit" in resp.headers


@patch("httpx.AsyncClient.request")
def test_gateway_rate_limit_exceeded_returns_429(mock_request, client, db_session):
    mock_request.return_value = httpx.Response(
        status_code=200,
        json={"message": "Hello from downstream service"},
    )

    # Create an isolated API key with strict limit of 3
    burst_key = ApiKey(
        key="pg_live_isolated_burst_key_123",
        name="Burst Test Key",
        user_id=1,
        rate_limit=3,
        is_active=True,
    )
    db_session.add(burst_key)
    db_session.commit()

    # Clear any cached rate-limit state for this key
    _in_memory_buckets.pop(burst_key.key, None)
    r = get_redis_client()
    if r:
        r.delete(f"pulsegate:rate_limit:{burst_key.key}")

    # First 3 requests must succeed
    for _ in range(3):
        resp = client.post(
            "/api/gateway/request",
            json={"target_url": "http://localhost:8000/demo/hello", "method": "GET"},
            headers={"X-API-Key": burst_key.key},
        )
        assert resp.status_code == 200

    # 4th request must be rate-limited with HTTP 429
    resp_blocked = client.post(
        "/api/gateway/request",
        json={"target_url": "http://localhost:8000/demo/hello", "method": "GET"},
        headers={"X-API-Key": burst_key.key},
    )
    assert resp_blocked.status_code == 429
    assert resp_blocked.json()["detail"] == "Rate limit exceeded"
    assert "retry_after" in resp_blocked.json()
    assert "Retry-After" in resp_blocked.headers
