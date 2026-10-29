"""Feature engineering for PulseGate ML Anomaly Detection.

Transforms raw request logs within a time window into a structured numerical feature vector:
1. request_count: Total number of requests in window
2. requests_per_second: Requests divided by window length in seconds
3. average_latency: Mean response latency in milliseconds
4. error_rate: Fraction of failed requests (4xx / 5xx) between 0.0 and 1.0
5. unique_endpoints: Count of distinct API paths accessed
6. status_5xx_count: Count of critical server errors (HTTP status >= 500)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.models.request_log import RequestLog

FEATURE_NAMES = [
    "request_count",
    "requests_per_second",
    "average_latency",
    "error_rate",
    "unique_endpoints",
    "status_5xx_count",
]


def extract_features_from_logs(logs: List[RequestLog], window_seconds: int = 60) -> List[float]:
    """Calculate 6-dimensional feature vector from a collection of request logs in a window."""
    if not logs:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    request_count = len(logs)
    rps = round(request_count / max(1.0, float(window_seconds)), 3)

    latencies = [log.latency_ms for log in logs]
    avg_latency = round(float(np.mean(latencies)), 2)

    error_count = sum(1 for log in logs if log.is_error)
    error_rate = round(error_count / request_count, 4)

    unique_endpoints = len(set(log.endpoint for log in logs))
    status_5xx_count = sum(1 for log in logs if log.status_code >= 500)

    return [
        float(request_count),
        float(rps),
        float(avg_latency),
        float(error_rate),
        float(unique_endpoints),
        float(status_5xx_count),
    ]


def extract_features_for_window(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    window_seconds: int = 60,
) -> List[float]:
    """Query logs within [start_time, end_time] and extract window feature vector."""
    logs = (
        db.query(RequestLog)
        .filter(RequestLog.timestamp >= start_time, RequestLog.timestamp <= end_time)
        .all()
    )
    return extract_features_from_logs(logs, window_seconds=window_seconds)


def generate_synthetic_baseline(n_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
    """Generate synthetic normal traffic data to bootstrap and train the Isolation Forest model.
    
    Normal traffic parameters:
    - request_count: 10 to 50 requests per minute
    - latency: 50 to 300 ms (mean ~150 ms)
    - error_rate: 0.00 to 0.05
    - unique_endpoints: 1 to 4
    - status_5xx_count: 0 (occasional 1)
    """
    np.random.seed(random_state)

    request_counts = np.random.randint(10, 51, size=n_samples)
    rps = np.round(request_counts / 60.0, 3)

    # Lognormal/normal latency distribution between 60 and 280 ms
    base_latency = np.random.normal(loc=140.0, scale=35.0, size=n_samples)
    avg_latencies = np.clip(base_latency, 50.0, 320.0).round(2)

    # Error rate: mostly 0, rarely up to 4%
    error_rates = np.clip(np.random.beta(a=0.5, b=20.0, size=n_samples) * 0.1, 0.0, 0.05).round(4)

    # Unique endpoints: 1 to 4
    unique_endpoints = np.random.randint(1, 5, size=n_samples)

    # 5xx counts: predominantly 0
    status_5xx_counts = np.random.choice([0, 1], size=n_samples, p=[0.97, 0.03])

    df = pd.DataFrame({
        "request_count": request_counts,
        "requests_per_second": rps,
        "average_latency": avg_latencies,
        "error_rate": error_rates,
        "unique_endpoints": unique_endpoints,
        "status_5xx_count": status_5xx_counts,
    })
    return df
