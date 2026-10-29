"""Metrics reporting routes for dashboard visualization."""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.metrics import MetricsSummaryResponse, TimeSeriesPoint, EndpointStat
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


def parse_time_range(time_range: Optional[str]) -> Optional[datetime]:
    """Convert time range filter into cutoff datetime."""
    if not time_range or time_range == "all":
        return None
    now = datetime.now(timezone.utc)
    if time_range == "5m":
        return now - timedelta(minutes=5)
    elif time_range == "15m":
        return now - timedelta(minutes=15)
    elif time_range == "1h":
        return now - timedelta(hours=1)
    elif time_range == "24h":
        return now - timedelta(hours=24)
    return None


@router.get("/summary", response_model=MetricsSummaryResponse)
def get_metrics_summary(
    time_range: Optional[str] = Query("1h", description="5m, 15m, 1h, 24h, all"),
    endpoint: Optional[str] = Query(None, description="Optional endpoint filter"),
    db: Session = Depends(get_db),
):
    """Return aggregated high-level performance metrics."""
    start_time = parse_time_range(time_range)
    return MetricsService.get_summary(db=db, start_time=start_time, endpoint=endpoint)


@router.get("/timeseries", response_model=List[TimeSeriesPoint])
def get_metrics_timeseries(
    time_range: Optional[str] = Query("1h", description="5m, 15m, 1h, 24h, all"),
    endpoint: Optional[str] = Query(None, description="Optional endpoint filter"),
    limit: int = Query(50, ge=5, le=200),
    db: Session = Depends(get_db),
):
    """Return timeseries metrics bucketed by minute for charting."""
    start_time = parse_time_range(time_range)
    return MetricsService.get_timeseries(db=db, start_time=start_time, endpoint=endpoint, limit=limit)


@router.get("/endpoints", response_model=List[EndpointStat])
def get_endpoint_statistics(db: Session = Depends(get_db)):
    """Return per-endpoint performance statistics."""
    return MetricsService.get_endpoints_stats(db=db)
