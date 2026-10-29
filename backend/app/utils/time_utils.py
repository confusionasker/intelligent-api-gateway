"""Time utility helpers for PulseGate metrics and windowing."""

from datetime import datetime, timezone, timedelta
from typing import Tuple


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def utc_iso_format(dt: datetime | None = None) -> str:
    """Format datetime into standard ISO-8601 string."""
    target = dt or utc_now()
    return target.isoformat()


def get_window_bounds(dt: datetime, window_seconds: int = 60) -> Tuple[datetime, datetime]:
    """Calculate the start and end of the fixed time window containing `dt`.
    
    Useful for bucketing metrics into 1-minute anomaly detection intervals.
    """
    timestamp = dt.timestamp()
    bucket_start_ts = int(timestamp // window_seconds) * window_seconds
    bucket_end_ts = bucket_start_ts + window_seconds
    start_dt = datetime.fromtimestamp(bucket_start_ts, tz=timezone.utc)
    end_dt = datetime.fromtimestamp(bucket_end_ts, tz=timezone.utc)
    return start_dt, end_dt
