"""
AEGISCORE — Backend Configuration
Self-Hosted AI Security Intelligence Platform
Author: Mohamed Adhnaan J M | BYTEAEGIS
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for AEGISCORE backend.
    All values are loaded from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aegiscore"
    POSTGRES_USER: str = "aegiscore"
    POSTGRES_PASSWORD: str = "aegiscore"
    DATABASE_URL: str = "postgresql+asyncpg://aegiscore:aegiscore@localhost:5432/aegiscore"

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Authentication ────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-64"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Celery ────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_WORKER_CONCURRENCY: int = 4

    # ── Ollama (Local LLM) ───────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "codellama:7b"
    OLLAMA_TIMEOUT: int = 120

    # ── ML Risk Model ────────────────────────────────────────────────────
    ML_MODEL_PATH: str = "/app/models/risk_model.pkl"
    ML_RETRAIN_EVERY_N_SCANS: int = 10
    ML_MIN_TRAINING_SAMPLES: int = 50

    # ── Scanners ─────────────────────────────────────────────────────────
    SEMGREP_RULES: str = "p/owasp-top-ten,p/python,p/javascript"
    TRIVY_SEVERITY: str = "HIGH,CRITICAL"

    # ── Slack Alerts ─────────────────────────────────────────────────────
    SLACK_WEBHOOK_URL: str = ""
    SLACK_ALERT_SEVERITY: str = "CRITICAL"

    # ── Prometheus ───────────────────────────────────────────────────────
    PROMETHEUS_ENABLED: bool = True

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "AEGISCORE"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False


settings = Settings()
