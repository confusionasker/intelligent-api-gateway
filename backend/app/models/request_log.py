"""Request Log model for tracking every gateway request and calculating metrics."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    endpoint = Column(String(255), index=True, nullable=False)
    method = Column(String(10), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True, index=True)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    is_error = Column(Boolean, default=False, index=True, nullable=False)

    api_key = relationship("ApiKey", back_populates="request_logs")

    # Composite index for time-window queries filtering by endpoint or errors
    __table_args__ = (
        Index("ix_request_logs_timestamp_endpoint", "timestamp", "endpoint"),
    )
