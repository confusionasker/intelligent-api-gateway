"""Pydantic schemas for metrics APIs."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class MetricsSummaryResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    average_latency_ms: float
    requests_per_second: float


class TimeSeriesPoint(BaseModel):
    timestamp: str
    requests: int
    average_latency_ms: float
    error_rate: float


class EndpointStat(BaseModel):
    endpoint: str
    requests: int
    average_latency_ms: float
    error_rate: float
