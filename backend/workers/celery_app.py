"""
AEGISCORE — Celery Application Configuration
Distributed task queue for scan, AI, and maintenance workers.
"""

from celery import Celery

from config import settings

app = Celery(
    "aegiscore",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    result_expires=3600,
    task_routes={
        "workers.tasks.scan_tasks.*": {"queue": "scans"},
        "workers.tasks.ai_tasks.*": {"queue": "ai"},
        "workers.tasks.maintenance_tasks.*": {"queue": "maintenance"},
    },
    task_default_queue="scans",
    task_default_exchange="aegiscore",
    task_default_routing_key="scans",
    # Explicitly import tasks
    imports=[
        "workers.tasks.scan_tasks",
        "workers.tasks.ai_tasks",
        "workers.tasks.maintenance_tasks",
    ],
)

# Alias for backwards compatibility if needed
celery_app = app



