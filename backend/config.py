"""
AEGISCORE — Backend Configuration
Self-Hosted AI Security Intelligence Platform
Author: Mohamed Adhnaan J M | BYTEAEGIS
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for AEGISCORE backend.
    All values are loaded from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aegiscore"
    POSTGRES_USER: str = "aegiscore"
    POSTGRES_PASSWORD: str = "aegiscore_secret"
    DATABASE_URL: str = (
        f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aegiscore.db').replace(chr(92), '/')}"
    )

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Authentication ────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-64"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:80", "http://localhost", "http://localhost:3000"]

    # ── Celery ────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_WORKER_CONCURRENCY: int = 4

    # ── Ollama (Local LLM) ───────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "stable-code:3b"
    OLLAMA_TIMEOUT: int = 120

    # ── ML Risk Model ────────────────────────────────────────────────────
    ML_MODEL_PATH: str = (
        "/app/ml_models/risk_model.pkl"
        if os.path.exists("/app")
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml_models", "risk_model.pkl")
    )
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
