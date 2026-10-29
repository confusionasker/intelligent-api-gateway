"""Anomaly detection API routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.anomaly import AnomalyResponse, LatestAnomalyStatus
from app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/api/anomalies", tags=["Anomaly Detection"])


@router.get("", response_model=List[AnomalyResponse])
def get_anomalies(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve historical traffic anomalies detected by Isolation Forest."""
    return AnomalyService.get_recent_anomalies(db=db, limit=limit)


@router.get("/latest", response_model=LatestAnomalyStatus)
def get_latest_anomaly_status(db: Session = Depends(get_db)):
    """Retrieve live traffic health status (NORMAL, WARNING, ANOMALY) and latest detected event."""
    status_data = AnomalyService.get_latest_status(db=db)
    return LatestAnomalyStatus(
        is_anomaly=status_data["is_anomaly"],
        status_label=status_data["status_label"],
        latest_anomaly=status_data["latest_anomaly"],
        window_stats=status_data["window_stats"],
    )


@router.post("/evaluate")
def evaluate_traffic_now(
    window_seconds: int = Query(60, ge=10, le=600),
    db: Session = Depends(get_db),
):
    """Trigger real-time Isolation Forest evaluation on recent traffic window immediately."""
    is_anomaly, anomaly_obj, stats = AnomalyService.evaluate_recent_window(db=db, window_seconds=window_seconds)
    return {
        "is_anomaly": is_anomaly,
        "anomaly_score": stats["anomaly_score"],
        "reason": stats["reason"],
        "anomaly_id": anomaly_obj.id if anomaly_obj else None,
        "window_stats": stats,
    }
