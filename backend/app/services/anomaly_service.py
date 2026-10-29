"""Anomaly detection service.

Orchestrates windowed log extraction, ML evaluation, anomaly persistence, and dashboard retrieval.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.request_log import RequestLog
from app.models.anomaly import Anomaly
from app.services.ml_service import MLService
from app.utils.logger import logger


class AnomalyService:
    @staticmethod
    def evaluate_recent_window(db: Session, window_seconds: int = 60) -> Tuple[bool, Optional[Anomaly], Dict[str, Any]]:
        """Extract traffic metrics for the past window_seconds, run ML detection, and persist if anomalous."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(seconds=window_seconds)

        logs = (
            db.query(RequestLog)
            .filter(RequestLog.timestamp >= start_time)
            .all()
        )

        # Evaluate window using ML service
        pred, score, reason, feature_vec = MLService.evaluate_traffic_logs(logs, window_seconds=window_seconds)
        is_anomaly = (pred == -1) and (len(logs) > 0)

        window_stats = {
            "window_seconds": window_seconds,
            "request_count": int(feature_vec[0]),
            "requests_per_second": feature_vec[1],
            "average_latency_ms": feature_vec[2],
            "error_rate": feature_vec[3],
            "unique_endpoints": int(feature_vec[4]),
            "status_5xx_count": int(feature_vec[5]),
            "anomaly_score": score,
            "prediction": pred,
            "reason": reason,
        }

        anomaly_record: Optional[Anomaly] = None

        if is_anomaly and len(logs) > 0:
            # Check if an anomaly was already recorded in the last 15 seconds to prevent flood
            recent_record = (
                db.query(Anomaly)
                .filter(Anomaly.timestamp >= now - timedelta(seconds=15))
                .first()
            )
            if not recent_record:
                anomaly_record = Anomaly(
                    timestamp=now,
                    request_count=int(feature_vec[0]),
                    average_latency_ms=feature_vec[2],
                    error_rate=feature_vec[3],
                    anomaly_score=score,
                    reason=reason,
                )
                db.add(anomaly_record)
                db.commit()
                db.refresh(anomaly_record)
                logger.warning(
                    f"[ALERT] ANOMALY DETECTED by Isolation Forest! Score={score:.4f}, Count={feature_vec[0]}, Reason={reason}"
                )
            else:
                anomaly_record = recent_record

        return is_anomaly, anomaly_record, window_stats

    @staticmethod
    def get_recent_anomalies(db: Session, limit: int = 50) -> List[Anomaly]:
        """Fetch list of historical anomalies sorted by timestamp descending."""
        return db.query(Anomaly).order_by(desc(Anomaly.timestamp)).limit(limit).all()

    @staticmethod
    def get_latest_status(db: Session) -> Dict[str, Any]:
        """Determine current health status for the live dashboard (NORMAL, WARNING, ANOMALY)."""
        is_anomaly, anomaly_record, window_stats = AnomalyService.evaluate_recent_window(db, window_seconds=60)

        # Retrieve the most recent recorded anomaly in database
        latest_db_anomaly = db.query(Anomaly).order_by(desc(Anomaly.timestamp)).first()

        # Determine status label safely handling naive/aware datetimes
        now = datetime.now(timezone.utc)
        if latest_db_anomaly:
            ts = latest_db_anomaly.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            anomaly_age = (now - ts).total_seconds()
        else:
            anomaly_age = 999999

        if is_anomaly:
            status_label = "ANOMALY"
        elif anomaly_age < 120:
            # If an anomaly occurred within the last 2 minutes, keep warning status active
            status_label = "WARNING"
        else:
            status_label = "NORMAL"

        active_record = anomaly_record or latest_db_anomaly

        return {
            "is_anomaly": (status_label == "ANOMALY"),
            "status_label": status_label,
            "latest_anomaly": active_record if status_label in ("ANOMALY", "WARNING") else None,
            "window_stats": window_stats,
        }
