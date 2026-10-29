"""Isolation Forest Prediction and Explainability Module.

Loads the trained scikit-learn model, executes inference on real-time traffic feature vectors,
and generates human-interpretable explanations of contributing anomalous signals.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from app.ml.feature_engineering import FEATURE_NAMES
from app.ml.train_model import train_isolation_forest, get_default_model_path
from app.utils.logger import logger

_loaded_model: Optional[IsolationForest] = None


def get_model(force_reload: bool = False) -> IsolationForest:
    """Return loaded Isolation Forest model, training bootstrap model if file does not exist."""
    global _loaded_model
    if _loaded_model is not None and not force_reload:
        return _loaded_model

    model_path = get_default_model_path()
    if not model_path.exists():
        logger.warning(f"Model file not found at {model_path}. Training initial baseline model...")
        _loaded_model = train_isolation_forest(save_path=model_path)
    else:
        logger.info(f"Loading Isolation Forest model from {model_path}...")
        _loaded_model = joblib.load(model_path)

    return _loaded_model


def explain_anomaly_reasons(features: List[float]) -> str:
    """Derive human-readable explanation from contributing feature metrics.
    
    Feature indices:
    0: request_count
    1: requests_per_second
    2: average_latency
    3: error_rate
    4: unique_endpoints
    5: status_5xx_count
    """
    request_count = features[0]
    avg_latency = features[2]
    error_rate = features[3]
    status_5xx = features[5]

    signals = []
    if request_count > 65.0:
        signals.append(f"Unusual traffic volume ({int(request_count)} req/min)")
    if avg_latency > 350.0:
        signals.append(f"Abnormal response latency ({avg_latency:.1f} ms)")
    if error_rate > 0.08:
        signals.append(f"High API error rate ({error_rate * 100:.1f}%)")
    if status_5xx > 2:
        signals.append(f"Excessive server 5xx errors ({int(status_5xx)})")

    if len(signals) > 1:
        return "Multiple traffic metrics deviated from normal baseline: " + "; ".join(signals)
    elif len(signals) == 1:
        return signals[0] + " detected."
    else:
        return "Statistical traffic anomaly identified by Isolation Forest multidimensional boundary."


def predict_traffic_window(feature_vector: List[float]) -> Tuple[int, float, str]:
    """Run Isolation Forest inference on a 6-feature traffic window.
    
    Args:
        feature_vector: [request_count, rps, avg_latency, error_rate, unique_endpoints, 5xx_count]
        
    Returns:
        Tuple of (prediction, anomaly_score, reason)
        - prediction: 1 (Normal) or -1 (Anomaly)
        - anomaly_score: raw decision function score (negative indicates anomaly)
        - reason: human-readable explanation
    """
    model = get_model()
    # Use DataFrame with feature names to adhere to sklearn best practices and avoid warnings
    df = pd.DataFrame([feature_vector], columns=FEATURE_NAMES)

    # scikit-learn IsolationForest:
    # predict() returns 1 for inlier (normal), -1 for outlier (anomaly)
    raw_pred = int(model.predict(df)[0])

    # decision_function() returns anomaly score: negative = outlier
    score = float(model.decision_function(df)[0])

    if raw_pred == -1:
        reason = explain_anomaly_reasons(feature_vector)
    else:
        reason = "Normal traffic profile"

    return raw_pred, round(score, 4), reason
