"""Machine Learning orchestration service.

Handles feature vector extraction, model execution, and format normalization.
"""

from typing import List, Tuple
from app.ml.predict import predict_traffic_window, get_model
from app.ml.feature_engineering import extract_features_from_logs
from app.models.request_log import RequestLog
from app.utils.logger import logger


class MLService:
    @staticmethod
    def ensure_model_ready():
        """Ensure model is loaded and ready for inference."""
        return get_model()

    @staticmethod
    def evaluate_traffic_logs(logs: List[RequestLog], window_seconds: int = 60) -> Tuple[int, float, str, List[float]]:
        """Extract features from logs and return (prediction, anomaly_score, reason, feature_vector)."""
        if not logs or len(logs) == 0:
            # Idle window (zero requests) is normal baseline, never an anomaly
            return 1, 0.5, "No traffic in window (Idle)", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        feature_vector = extract_features_from_logs(logs, window_seconds=window_seconds)
        pred, score, reason = predict_traffic_window(feature_vector)
        return pred, score, reason, feature_vector
