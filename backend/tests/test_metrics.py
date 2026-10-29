"""Tests for request logging, analytical aggregates, timeseries, and endpoint breakdown."""

from app.services.metrics_service import MetricsService


def test_metrics_logged_and_summary_computed(client, db_session):
    # Log 3 successful requests and 1 error
    MetricsService.record_request(
        db=db_session,
        endpoint="/demo/hello",
        method="GET",
        status_code=200,
        latency_ms=105.0,
        api_key_id=1,
    )
    MetricsService.record_request(
        db=db_session,
        endpoint="/demo/hello",
        method="GET",
        status_code=200,
        latency_ms=95.0,
        api_key_id=1,
    )
    MetricsService.record_request(
        db=db_session,
        endpoint="/demo/slow",
        method="GET",
        status_code=200,
        latency_ms=350.0,
        api_key_id=1,
    )
    MetricsService.record_request(
        db=db_session,
        endpoint="/demo/error",
        method="GET",
        status_code=500,
        latency_ms=45.0,
        api_key_id=1,
    )

    # Test /api/metrics/summary
    summary_resp = client.get("/api/metrics/summary?time_range=all")
    assert summary_resp.status_code == 200
    data = summary_resp.json()
    assert data["total_requests"] == 4
    assert data["successful_requests"] == 3
    assert data["failed_requests"] == 1
    assert data["error_rate"] == 25.0
    assert data["average_latency_ms"] > 0


def test_metrics_timeseries_api(client, db_session):
    MetricsService.record_request(
        db=db_session,
        endpoint="/demo/hello",
        method="GET",
        status_code=200,
        latency_ms=110.0,
    )

    resp = client.get("/api/metrics/timeseries?time_range=all")
    assert resp.status_code == 200
    points = resp.json()
    assert len(points) >= 1
    assert "requests" in points[0]
    assert "average_latency_ms" in points[0]


def test_metrics_endpoints_api(client, db_session):
    MetricsService.record_request(
        db=db_session,
        endpoint="/api/v1/users",
        method="GET",
        status_code=200,
        latency_ms=80.0,
    )
    MetricsService.record_request(
        db=db_session,
        endpoint="/api/v1/orders",
        method="POST",
        status_code=201,
        latency_ms=140.0,
    )

    resp = client.get("/api/metrics/endpoints")
    assert resp.status_code == 200
    endpoints = resp.json()
    assert len(endpoints) >= 2
    paths = [e["endpoint"] for e in endpoints]
    assert "/api/v1/users" in paths
    assert "/api/v1/orders" in paths
