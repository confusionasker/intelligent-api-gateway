"""Metrics service for recording gateway requests and computing analytical aggregates."""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.request_log import RequestLog
from app.schemas.metrics import MetricsSummaryResponse, TimeSeriesPoint, EndpointStat
from app.utils.logger import logger


class MetricsService:
    @staticmethod
    def record_request(
        db: Session,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
        api_key_id: Optional[int] = None,
        is_error: Optional[bool] = None,
        dt: Optional[datetime] = None,
    ) -> RequestLog:
        """Persist a single gateway request event into the database."""
        timestamp = dt or datetime.now(timezone.utc)
        error_flag = is_error if is_error is not None else (status_code >= 400)

        log_entry = RequestLog(
            timestamp=timestamp,
            endpoint=endpoint,
            method=method.upper(),
            api_key_id=api_key_id,
            status_code=status_code,
            latency_ms=round(latency_ms, 2),
            is_error=error_flag,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_summary(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        endpoint: Optional[str] = None,
    ) -> MetricsSummaryResponse:
        """Compute aggregated metrics (total, success, failed, error rate, average latency, RPS)."""
        query = db.query(
            func.count(RequestLog.id).label("total"),
            func.sum(case((RequestLog.is_error == False, 1), else_=0)).label("success"),
            func.sum(case((RequestLog.is_error == True, 1), else_=0)).label("failed"),
            func.avg(RequestLog.latency_ms).label("avg_latency"),
            func.min(RequestLog.timestamp).label("first_ts"),
            func.max(RequestLog.timestamp).label("last_ts"),
        )

        if start_time:
            query = query.filter(RequestLog.timestamp >= start_time)
        if end_time:
            query = query.filter(RequestLog.timestamp <= end_time)
        if endpoint:
            query = query.filter(RequestLog.endpoint == endpoint)

        row = query.first()
        total = row.total or 0
        success = row.success or 0
        failed = row.failed or 0
        avg_lat = round(float(row.avg_latency or 0.0), 2)
        error_rate = round((failed / total * 100.0) if total > 0 else 0.0, 2)

        # Requests per second calculation
        if total > 0 and row.first_ts and row.last_ts:
            delta_seconds = max(1.0, (row.last_ts - row.first_ts).total_seconds())
            rps = round(total / delta_seconds, 2)
        else:
            rps = 0.0

        return MetricsSummaryResponse(
            total_requests=total,
            successful_requests=success,
            failed_requests=failed,
            error_rate=error_rate,
            average_latency_ms=avg_lat,
            requests_per_second=rps,
        )

    @staticmethod
    def get_timeseries(
        db: Session,
        start_time: Optional[datetime] = None,
        endpoint: Optional[str] = None,
        limit: int = 30,
    ) -> List[TimeSeriesPoint]:
        """Aggregate request metrics into time buckets (1-minute or recent timestamps) for charting."""
        if not start_time:
            start_time = datetime.now(timezone.utc) - timedelta(minutes=60)

        query = db.query(RequestLog).filter(RequestLog.timestamp >= start_time)
        if endpoint:
            query = query.filter(RequestLog.endpoint == endpoint)

        logs = query.order_by(RequestLog.timestamp.asc()).all()

        if not logs:
            return []

        # Bucket by minute in Indian Standard Time (IST, UTC+05:30)
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        buckets: Dict[str, Dict[str, Any]] = {}
        for log in logs:
            ts = log.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            bucket_key = ts.astimezone(ist_tz).strftime("%H:%M")
            if bucket_key not in buckets:
                buckets[bucket_key] = {"requests": 0, "latencies": [], "errors": 0}
            buckets[bucket_key]["requests"] += 1
            buckets[bucket_key]["latencies"].append(log.latency_ms)
            if log.is_error:
                buckets[bucket_key]["errors"] += 1

        points = []
        for bucket_key, val in sorted(buckets.items()):
            count = val["requests"]
            avg_lat = round(sum(val["latencies"]) / count, 2) if count else 0.0
            err_rate = round((val["errors"] / count * 100.0) if count else 0.0, 2)
            points.append(TimeSeriesPoint(
                timestamp=bucket_key,
                requests=count,
                average_latency_ms=avg_lat,
                error_rate=err_rate,
            ))

        return points[-limit:]

    @staticmethod
    def get_endpoints_stats(db: Session) -> List[EndpointStat]:
        """Group metrics by endpoint to show traffic distribution and performance."""
        results = db.query(
            RequestLog.endpoint,
            func.count(RequestLog.id).label("total"),
            func.avg(RequestLog.latency_ms).label("avg_lat"),
            func.sum(case((RequestLog.is_error == True, 1), else_=0)).label("errors"),
        ).group_by(RequestLog.endpoint).all()

        stats = []
        for row in results:
            total = row.total or 0
            errors = row.errors or 0
            err_rate = round((errors / total * 100.0) if total else 0.0, 2)
            stats.append(EndpointStat(
                endpoint=row.endpoint,
                requests=total,
                average_latency_ms=round(float(row.avg_lat or 0.0), 2),
                error_rate=err_rate,
            ))
        return stats
