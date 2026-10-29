"""Tests for Isolation Forest model inference, feature engineering, and anomaly detection."""

from datetime import datetime, timezone
from app.ml.predict import get_model, predict_traffic_window, explain_anomaly_reasons
from app.ml.feature_engineering import extract_features_from_logs, FEATURE_NAMES
from app.models.request_log import RequestLog
from app.models.anomaly import Anomaly


def test_ml_model_loads_successfully():
    model = get_model()
    assert model is not None
    assert hasattr(model, "predict")
    assert hasattr(model, "decision_function")


def test_feature_engineering_vector_shape():
    logs = [
        RequestLog(
            endpoint="/demo/hello",
            method="GET",
            status_code=200,
            latency_ms=120.0,
            is_error=False,
            timestamp=datetime.now(timezone.utc),
        ),
        RequestLog(
            endpoint="/demo/hello",
            method="GET",
            status_code=500,
            latency_ms=250.0,
            is_error=True,
            timestamp=datetime.now(timezone.utc),
        ),
    ]
    vec = extract_features_from_logs(logs, window_seconds=60)
    assert len(vec) == len(FEATURE_NAMES)
    assert vec[0] == 2.0  # request_count
    assert vec[2] == 185.0  # average_latency
    assert vec[3] == 0.5  # error_rate (1 error out of 2)
    assert vec[4] == 1.0  # unique_endpoints
    assert vec[5] == 1.0  # 5xx count


def test_normal_traffic_predicted_as_1():
    # Feature vector matching typical normal traffic:
    # 25 reqs/min, 0.42 RPS, 130ms latency, 0 error rate, 2 endpoints, 0 5xx
    normal_vector = [25.0, 0.42, 130.0, 0.0, 2.0, 0.0]
    pred, score, reason = predict_traffic_window(normal_vector)

    assert pred == 1  # 1 = Inlier / Normal
    assert "Normal traffic profile" in reason


def test_spike_traffic_predicted_as_anomaly_negative_1():
    # Feature vector depicting a severe anomaly:
    # 550 reqs/min (extreme burst), 9.17 RPS, 850ms latency, 25% error rate, 3 endpoints, 12 5xx
    spike_vector = [550.0, 9.17, 850.0, 0.25, 3.0, 12.0]
    pred, score, reason = predict_traffic_window(spike_vector)

    assert pred == -1  # -1 = Outlier / Anomaly
    assert score < 0.0  # Negative decision score indicates anomaly
    assert "Unusual traffic volume" in reason or "Multiple" in reason


def test_anomaly_reasoning_explanation():
    # High latency only
    reason_latency = explain_anomaly_reasons([20.0, 0.33, 750.0, 0.0, 1.0, 0.0])
    assert "Abnormal response latency" in reason_latency

    # High error rate only
    reason_error = explain_anomaly_reasons([20.0, 0.33, 100.0, 0.30, 1.0, 0.0])
    assert "High API error rate" in reason_error


def test_anomalies_api_endpoints(client, db_session):
    # Seed an anomaly in DB
    anomaly = Anomaly(
        timestamp=datetime.now(timezone.utc),
        request_count=450,
        average_latency_ms=620.5,
        error_rate=0.15,
        anomaly_score=-0.45,
        reason="Abnormal traffic volume detected",
    )
    db_session.add(anomaly)
    db_session.commit()

    # Query GET /api/anomalies
    resp = client.get("/api/anomalies")
    assert resp.status_code == 200
    anomalies = resp.json()
    assert len(anomalies) >= 1
    assert anomalies[0]["request_count"] == 450
    assert anomalies[0]["anomaly_score"] == -0.45

    # Query GET /api/anomalies/latest
    latest_resp = client.get("/api/anomalies/latest")
    assert latest_resp.status_code == 200
    status_data = latest_resp.json()
    assert status_data["status_label"] in ("NORMAL", "WARNING", "ANOMALY")
