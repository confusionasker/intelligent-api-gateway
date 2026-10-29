"""API Key model for gateway client authentication and rate limit policies."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(100), default="Primary Key", nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    rate_limit = Column(Integer, default=20, nullable=False)  # requests per window
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="api_keys")
    request_logs = relationship("RequestLog", back_populates="api_key")
