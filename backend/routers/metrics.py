"""
AEGISCORE — Metrics Router
Prometheus text format metrics endpoint.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from config import settings

router = APIRouter(tags=["Metrics"])

# ── Custom Prometheus registry ──────────────────────────────────────────────
registry = CollectorRegistry()

# ── Counters ────────────────────────────────────────────────────────────────
SCANS_TOTAL = Counter(
    "aegiscore_scans_total",
    "Total number of scans triggered",
    ["status"],
    registry=registry,
)

FINDINGS_TOTAL = Counter(
    "aegiscore_findings_total",
    "Total number of security findings detected",
    ["severity", "scanner"],
    registry=registry,
)

FIXES_GENERATED = Counter(
    "aegiscore_fixes_generated_total",
    "Total number of AI fix suggestions generated",
    ["confidence"],
    registry=registry,
)

FIXES_APPLIED = Counter(
    "aegiscore_fixes_applied_total",
    "Total number of AI fix suggestions applied",
    registry=registry,
)

# ── Histograms ──────────────────────────────────────────────────────────────
SCAN_DURATION = Histogram(
    "aegiscore_scan_duration_seconds",
    "Scan duration in seconds",
    ["scanner"],
    buckets=[5, 10, 30, 60, 120, 300, 600],
    registry=registry,
)

FIX_GENERATION_DURATION = Histogram(
    "aegiscore_fix_generation_duration_seconds",
    "Fix generation duration in seconds",
    buckets=[5, 10, 30, 60, 120],
    registry=registry,
)

# ── Gauges ──────────────────────────────────────────────────────────────────
QUEUE_DEPTH = Gauge(
    "aegiscore_queue_depth",
    "Current depth of task queues",
    ["queue"],
    registry=registry,
)

WORKER_COUNT = Gauge(
    "aegiscore_worker_count",
    "Number of active Celery workers",
    ["queue"],
    registry=registry,
)

ML_ACCURACY = Gauge(
    "aegiscore_ml_accuracy",
    "ML model accuracy metrics",
    ["metric"],
    registry=registry,
)

RISK_SCORE_GAUGE = Gauge(
    "aegiscore_risk_score",
    "Current risk score for a file",
    ["repo", "file_path"],
    registry=registry,
)

ACTIVE_SCANS = Gauge(
    "aegiscore_active_scans",
    "Number of currently running scans",
    registry=registry,
)


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """
    Return Prometheus text format metrics.
    Scraped by Prometheus at /metrics endpoint.
    """
    if not settings.PROMETHEUS_ENABLED:
        return PlainTextResponse(
            content="# Prometheus metrics disabled\n",
            media_type="text/plain",
        )

    return PlainTextResponse(
        content=generate_latest(registry).decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )
