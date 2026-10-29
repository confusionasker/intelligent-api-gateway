"""PulseGate API Gateway Application Entry Point.

Combines routing, rate limiting, metrics tracking, machine learning anomaly detection,
and automated database initialization.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.init_db import init_db
from app.db.database import SessionLocal
from app.ml.predict import get_model
from app.services.anomaly_service import AnomalyService
from app.api.routes_auth import router as auth_router
from app.api.routes_gateway import router as gateway_router
from app.api.routes_metrics import router as metrics_router
from app.api.routes_anomaly import router as anomaly_router
from app.api.routes_health import router as health_router
from app.utils.logger import logger


# Background worker for continuous traffic anomaly detection
async def continuous_anomaly_monitor():
    """Periodically evaluate recent traffic window to detect and log traffic anomalies."""
    logger.info("Background anomaly monitoring worker started.")
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            db = SessionLocal()
            try:
                is_anomaly, anomaly_record, stats = AnomalyService.evaluate_recent_window(db, window_seconds=60)
                if is_anomaly:
                    logger.warning(f"Background detector identified traffic anomaly: {stats.get('reason')}")
            finally:
                db.close()
        except asyncio.CancelledError:
            logger.info("Background anomaly monitor stopping...")
            break
        except Exception as exc:
            logger.error(f"Error in background anomaly monitor: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown hooks."""
    logger.info("Starting PulseGate API Gateway...")
    # 1. Initialize SQLite database & seed default user
    init_db()

    # 2. Bootstrap ML model
    get_model()

    # 3. Spawn background anomaly detection task
    monitor_task = asyncio.create_task(continuous_anomaly_monitor())

    yield

    # Shutdown
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
    logger.info("PulseGate API Gateway shut down gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent API Gateway with Token Bucket Rate Limiting and Isolation Forest Anomaly Detection",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Centralized Error Handlers
# ---------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Centralized HTTP exception formatter."""
    detail = exc.detail
    headers = exc.headers or {}

    # Map status codes to readable error codes
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        408: "REQUEST_TIMEOUT",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        504: "GATEWAY_TIMEOUT",
    }
    error_code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")

    # Standardize error message
    message = detail if isinstance(detail, str) else detail.get("detail", str(detail))

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
            },
        },
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Centralized request validation error formatter."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": exc.errors(),
            },
        },
    )


# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(gateway_router)
app.include_router(metrics_router)
app.include_router(anomaly_router)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "architecture": "Token Bucket Rate Limiting + Isolation Forest ML Anomaly Detection",
        "gateway_mode": "Open Proxy",
    }

