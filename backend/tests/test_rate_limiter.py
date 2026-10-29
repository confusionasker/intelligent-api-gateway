"""Tests for API Key lifecycle and Token Bucket rate limiting."""

from app.services.rate_limiter import TokenBucketRateLimiter


def test_api_key_generation_and_listing(client):
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "testpass123"},
    )
    token = login_resp.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # Create new API key
    create_resp = client.post(
        "/api/keys",
        json={"name": "Production Key", "rate_limit": 50},
        headers=auth_header,
    )
    assert create_resp.status_code == 201
    key_data = create_resp.json()
    assert key_data["key"].startswith("pg_live_")
    assert key_data["name"] == "Production Key"
    assert key_data["rate_limit"] == 50

    # List keys
    list_resp = client.get("/api/keys", headers=auth_header)
    assert list_resp.status_code == 200
    keys = list_resp.json()
    assert len(keys) >= 2


def test_api_key_deactivation(client):
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "testpass123"},
    )
    token = login_resp.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # Fetch existing key ID
    list_resp = client.get("/api/keys", headers=auth_header)
    key_id = list_resp.json()[0]["id"]

    # Deactivate key
    del_resp = client.delete(f"/api/keys/{key_id}", headers=auth_header)
    assert del_resp.status_code == 200
    assert "deactivated" in del_resp.json()["message"]


def test_token_bucket_allows_within_capacity():
    limiter = TokenBucketRateLimiter(default_rate_limit=10, window_seconds=60)
    key = "unit_test_key_allow"

    for i in range(10):
        result = limiter.check_rate_limit(key=key, capacity=10)
        assert result.allowed is True
        assert result.remaining == 9 - i


def test_token_bucket_exceed_capacity_returns_429():
    limiter = TokenBucketRateLimiter(default_rate_limit=3, window_seconds=60)
    key = "unit_test_key_exceed"

    # Consume all 3 tokens
    assert limiter.check_rate_limit(key=key, capacity=3).allowed is True
    assert limiter.check_rate_limit(key=key, capacity=3).allowed is True
    assert limiter.check_rate_limit(key=key, capacity=3).allowed is True

    # 4th request must be rejected
    res = limiter.check_rate_limit(key=key, capacity=3)
    assert res.allowed is False
    assert res.remaining == 0
    assert res.retry_after > 0


def test_rate_limit_headers_format():
    limiter = TokenBucketRateLimiter(default_rate_limit=5, window_seconds=60)
    result = limiter.check_rate_limit(key="headers_test_key", capacity=5)
    headers = result.get_headers()

    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers
    assert "X-RateLimit-Reset" in headers
    assert headers["X-RateLimit-Limit"] == "5"
    assert headers["X-RateLimit-Remaining"] == "4"
