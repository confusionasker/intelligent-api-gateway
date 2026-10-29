from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_serializer

# Indian Standard Time (IST, UTC+05:30)
IST = timezone(timedelta(hours=5, minutes=30))


class AnomalyResponse(BaseModel):
    id: int
    timestamp: datetime
    request_count: int
    average_latency_ms: float
    error_rate: float
    anomaly_score: float
    reason: str

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp")
    def serialize_timestamp(self, dt: datetime, _info):
        """Serialize timestamp to Indian Standard Time (IST, UTC+05:30)."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).isoformat()


class LatestAnomalyStatus(BaseModel):
    is_anomaly: bool
    status_label: str  # "NORMAL", "WARNING", "ANOMALY"
    latest_anomaly: Optional[AnomalyResponse] = None
    window_stats: Optional[dict] = None
