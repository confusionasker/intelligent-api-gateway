"""Anomaly model storing detected traffic anomalies and ML output."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from app.db.database import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    request_count = Column(Integer, nullable=False)
    average_latency_ms = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    reason = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
