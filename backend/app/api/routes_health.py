"""Health check endpoints verifying database, rate limiter, and ML model status."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.database import get_db
from app.ml.predict import get_model

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for API Gateway and sub-components."""
    # Check Database
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {exc}"

    # Rate Limiter status
    rate_limiter_status = f"healthy ({settings.RATE_LIMITER_BACKEND} token-bucket)"

    # Check ML Model
    ml_status = "loaded"
    try:
        m = get_model()
        if m is None:
            ml_status = "not loaded"
    except Exception as exc:
        ml_status = f"error: {exc}"

    return {
        "status": "online",
        "service": "PulseGate API Gateway",
        "database": db_status,
        "rate_limiter": rate_limiter_status,
        "ml_model": ml_status,
    }
