"""Application configuration module using Pydantic Settings.

Reads configuration from environment variables or .env file with defaults.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PulseGate API Gateway"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # SQLite database URL
    DATABASE_URL: str = "sqlite:///./pulsegate.db"

    # Rate Limiter backend: "memory" (default, zero external setup) or "redis"
    RATE_LIMITER_BACKEND: str = "memory"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security & Auth
    JWT_SECRET: str = "pulsegate_super_secret_jwt_key_2026_dse_sp"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Rate Limiter defaults
    DEFAULT_RATE_LIMIT: int = 20  # requests per window
    RATE_WINDOW_SECONDS: int = 60  # seconds

    # Gateway downstream security allowlist ('*' allows testing any external public API or internal URL)
    ALLOWED_TARGET_HOSTS: str = "*"

    # ML Anomaly Detection settings
    MODEL_PATH: str = "app/ml/model/isolation_forest.joblib"
    ANOMALY_CONTAMINATION: float = 0.03
    ANOMALY_WINDOW_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [h.strip().lower() for h in self.ALLOWED_TARGET_HOSTS.split(",") if h.strip()]


settings = Settings()
