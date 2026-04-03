"""
AEGISCORE — Maintenance Celery Tasks
Model retraining and scheduled maintenance tasks.
"""

import logging
from datetime import datetime, timezone

from workers.celery_app import celery_app

logger = logging.getLogger("aegiscore.tasks.maintenance")


def _get_sync_session():
    """Create a synchronous database session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import settings

    sync_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    ).replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(sync_url, pool_size=5, max_overflow=10)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionLocal()


@celery_app.task(
    name="workers.tasks.maintenance_tasks.retrain_model_task",
    bind=True,
    max_retries=1,
    default_retry_delay=300,
)
def retrain_model_task(self):
    """
    Retrain the ML risk model using accumulated scan data.

    Training data is built from:
    - file_path + feature_snapshot from RiskScore records
    - had_vuln_next_scan: whether the file had findings in subsequent scans

    Only retrains if sufficient training samples are available.
    """
    db = _get_sync_session()
    try:
        from config import settings
        from models.finding import Finding
        from models.risk import RiskScore
        from models.scan import Scan
        from services.ai.risk_model import RiskModel

        # Build training data
        risk_scores = db.query(RiskScore).all()

        if len(risk_scores) < settings.ML_MIN_TRAINING_SAMPLES:
            logger.info(
                "Insufficient training data: %d samples (need %d)",
                len(risk_scores),
                settings.ML_MIN_TRAINING_SAMPLES,
            )
            return {
                "status": "skipped",
                "reason": "insufficient_data",
                "samples": len(risk_scores),
                "required": settings.ML_MIN_TRAINING_SAMPLES,
            }

        training_data = []

        for rs in risk_scores:
            # Check if the file had vulnerabilities in scans after risk was calculated
            subsequent_findings = (
                db.query(Finding)
                .join(Scan, Finding.scan_id == Scan.id)
                .filter(
                    Finding.file_path == rs.file_path,
                    Scan.repo_id == rs.repo_id,
                    Scan.triggered_at > rs.calculated_at,
                )
                .count()
            )

            features = rs.feature_snapshot.copy() if rs.feature_snapshot else {}
            features["had_vuln_next_scan"] = subsequent_findings > 0

            training_data.append(features)

        # Train model
        model = RiskModel(settings.ML_MODEL_PATH)
        metrics = model.train(training_data)

        # Update Prometheus metrics
        try:
            from routers.metrics import ML_ACCURACY

            ML_ACCURACY.labels(metric="precision").set(metrics["precision"])
            ML_ACCURACY.labels(metric="recall").set(metrics["recall"])
            ML_ACCURACY.labels(metric="f1_score").set(metrics["f1_score"])
        except Exception:
            pass

        logger.info(
            "Model retrained: version=%s samples=%d precision=%.3f recall=%.3f f1=%.3f",
            metrics["model_version"],
            metrics["training_samples"],
            metrics["precision"],
            metrics["recall"],
            metrics["f1_score"],
        )

        return {
            "status": "completed",
            "model_version": metrics["model_version"],
            "training_samples": metrics["training_samples"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1_score"],
        }

    except Exception as e:
        logger.error("Model retraining failed: %s", e)
        raise
    finally:
        db.close()


@celery_app.task(
    name="workers.tasks.maintenance_tasks.cleanup_old_scans_task",
    bind=True,
)
def cleanup_old_scans_task(self, days_to_keep: int = 90):
    """
    Clean up scan data older than the specified number of days.
    Removes old scan records, findings, and risk history.
    """
    from datetime import timedelta

    db = _get_sync_session()
    try:
        from models.scan import Scan

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        # Count old scans
        old_scans = db.query(Scan).filter(
            Scan.triggered_at < cutoff
        ).count()

        if old_scans == 0:
            logger.info("No old scans to clean up")
            return {"deleted": 0}

        # Delete old scans (cascade deletes findings, tasks, etc.)
        db.query(Scan).filter(
            Scan.triggered_at < cutoff
        ).delete(synchronize_session=False)

        db.commit()

        logger.info("Cleaned up %d old scans (older than %d days)", old_scans, days_to_keep)
        return {"deleted": old_scans}

    except Exception as e:
        db.rollback()
        logger.error("Scan cleanup failed: %s", e)
        raise
    finally:
        db.close()


@celery_app.task(
    name="workers.tasks.maintenance_tasks.health_check_task",
    bind=True,
)
def health_check_task(self):
    """
    Simple health check task to verify worker connectivity.
    Returns system status information.
    """
    import platform

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }
