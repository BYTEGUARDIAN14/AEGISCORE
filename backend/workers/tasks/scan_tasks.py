"""
AEGISCORE — Scan Celery Tasks
Scanner execution tasks (semgrep, bandit, trivy) and scan finalization.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from workers.celery_app import celery_app

logger = logging.getLogger("aegiscore.tasks.scan")


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
    name="workers.tasks.scan_tasks.run_semgrep_task",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def run_semgrep_task(self, scan_task_id: str, scan_id: str, repo_path: str, rules: str):
    """
    Execute Semgrep scanner and store findings.

    Args:
        scan_task_id: UUID of the ScanTask record.
        scan_id: UUID of the parent Scan record.
        repo_path: Path to the cloned repository.
        rules: Semgrep rule configuration string.
    """
    import asyncio

    db = _get_sync_session()
    try:
        from models.scan import ScanTask, ScanStatus
        from models.finding import Finding, Severity

        # Update task status to running
        db.execute(
            update(ScanTask)
            .where(ScanTask.id == scan_task_id)
            .values(
                status=ScanStatus.running,
                started_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        # Run semgrep
        from services.scanner.semgrep import run_semgrep

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            findings = loop.run_until_complete(run_semgrep(repo_path, rules))
        finally:
            loop.close()

        # Insert findings
        for finding_data in findings:
            finding = Finding(
                scan_id=UUID(scan_id),
                scanner=finding_data["scanner"],
                severity=Severity(finding_data["severity"]),
                rule_id=finding_data["rule_id"],
                file_path=finding_data["file_path"],
                line_number=finding_data["line_number"],
                message=finding_data["message"],
                cwe=finding_data.get("cwe"),
                metadata=finding_data.get("metadata", {}),
            )
            db.add(finding)

        # Update task status
        db.execute(
            update(ScanTask)
            .where(ScanTask.id == scan_task_id)
            .values(
                status=ScanStatus.completed,
                completed_at=datetime.now(timezone.utc),
                findings_count=len(findings),
            )
        )
        db.commit()

        logger.info(
            "Semgrep scan completed: scan=%s findings=%d",
            scan_id,
            len(findings),
        )
        return {"scanner": "semgrep", "findings_count": len(findings)}

    except Exception as e:
        db.rollback()
        # Update task status to failed
        try:
            from models.scan import ScanTask, ScanStatus

            db.execute(
                update(ScanTask)
                .where(ScanTask.id == scan_task_id)
                .values(
                    status=ScanStatus.failed,
                    completed_at=datetime.now(timezone.utc),
                    error_message=str(e)[:500],
                )
            )
            db.commit()
        except Exception:
            db.rollback()

        logger.error("Semgrep scan failed: scan=%s error=%s", scan_id, e)
        raise
    finally:
        db.close()


@celery_app.task(
    name="workers.tasks.scan_tasks.run_bandit_task",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def run_bandit_task(self, scan_task_id: str, scan_id: str, repo_path: str):
    """Execute Bandit scanner and store findings."""
    import asyncio

    db = _get_sync_session()
    try:
        from models.scan import ScanTask, ScanStatus
        from models.finding import Finding, Severity

        # Update task status to running
        db.execute(
            update(ScanTask)
            .where(ScanTask.id == scan_task_id)
            .values(
                status=ScanStatus.running,
                started_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        # Run bandit
        from services.scanner.bandit import run_bandit

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            findings = loop.run_until_complete(run_bandit(repo_path))
        finally:
            loop.close()

        # Insert findings
        for finding_data in findings:
            finding = Finding(
                scan_id=UUID(scan_id),
                scanner=finding_data["scanner"],
                severity=Severity(finding_data["severity"]),
                rule_id=finding_data["rule_id"],
                file_path=finding_data["file_path"],
                line_number=finding_data["line_number"],
                message=finding_data["message"],
                cwe=finding_data.get("cwe"),
                metadata=finding_data.get("metadata", {}),
            )
            db.add(finding)

        # Update task status
        db.execute(
            update(ScanTask)
            .where(ScanTask.id == scan_task_id)
            .values(
                status=ScanStatus.completed,
                completed_at=datetime.now(timezone.utc),
                findings_count=len(findings),
            )
        )
        db.commit()

        logger.info(
            "Bandit scan completed: scan=%s findings=%d",
            scan_id,
            len(findings),
        )
        return {"scanner": "bandit", "findings_count": len(findings)}

    except Exception as e:
        db.rollback()
        try:
            from models.scan import ScanTask, ScanStatus

            db.execute(
                update(ScanTask)
                .where(ScanTask.id == scan_task_id)
                .values(
                    status=ScanStatus.failed,
                    completed_at=datetime.now(timezone.utc),
                    error_message=str(e)[:500],
                )
            )
            db.commit()
        except Exception:
            db.rollback()

        logger.error("Bandit scan failed: scan=%s error=%s", scan_id, e)
        raise
    finally:
        db.close()


@celery_app.task(
    name="workers.tasks.scan_tasks.run_trivy_task",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def run_trivy_task(self, scan_task_id: str, scan_id: str, repo_path: str):
    """Execute Trivy scanner and store findings."""
    import asyncio

    db = _get_sync_session()
    try:
        from models.scan import ScanTask, ScanStatus
        from models.finding import Finding, Severity

        # Update task status to running
        db.execute(
            update(ScanTask)
            .where(ScanTask.id == scan_task_id)
            .values(
                status=ScanStatus.running,
                started_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        # Run trivy
        from services.scanner.trivy import run_trivy

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            findings = loop.run_until_complete(run_trivy(repo_path))
        finally:
            loop.close()

        # Insert findings
        for finding_data in findings:
            finding = Finding(
                scan_id=UUID(scan_id),
                scanner=finding_data["scanner"],
                severity=Severity(finding_data["severity"]),
                rule_id=finding_data["rule_id"],
                file_path=finding_data["file_path"],
                line_number=finding_data["line_number"],
                message=finding_data["message"],
                cwe=finding_data.get("cwe"),
                metadata=finding_data.get("metadata", {}),
            )
            db.add(finding)

        # Update task status
        db.execute(
            update(ScanTask)
            .where(ScanTask.id == scan_task_id)
            .values(
                status=ScanStatus.completed,
                completed_at=datetime.now(timezone.utc),
                findings_count=len(findings),
            )
        )
        db.commit()

        logger.info(
            "Trivy scan completed: scan=%s findings=%d",
            scan_id,
            len(findings),
        )
        return {"scanner": "trivy", "findings_count": len(findings)}

    except Exception as e:
        db.rollback()
        try:
            from models.scan import ScanTask, ScanStatus

            db.execute(
                update(ScanTask)
                .where(ScanTask.id == scan_task_id)
                .values(
                    status=ScanStatus.failed,
                    completed_at=datetime.now(timezone.utc),
                    error_message=str(e)[:500],
                )
            )
            db.commit()
        except Exception:
            db.rollback()

        logger.error("Trivy scan failed: scan=%s error=%s", scan_id, e)
        raise
    finally:
        db.close()


@celery_app.task(
    name="workers.tasks.scan_tasks.finalize_scan_task",
    bind=True,
)
def finalize_scan_task(self, scanner_results: list, scan_id: str):
    """
    Finalize scan after all scanners complete.
    Called as a Celery chord callback.

    Aggregates findings counts, updates Scan record, runs correlation,
    enqueues AI tasks (risk scoring and fix generation).
    """
    import asyncio

    db = _get_sync_session()
    try:
        from models.scan import Scan, ScanStatus
        from models.finding import Finding, Severity

        scan_uuid = UUID(scan_id)

        # Count findings by severity
        critical = db.query(Finding).filter(
            Finding.scan_id == scan_uuid,
            Finding.severity == Severity.CRITICAL,
        ).count()

        high = db.query(Finding).filter(
            Finding.scan_id == scan_uuid,
            Finding.severity == Severity.HIGH,
        ).count()

        medium = db.query(Finding).filter(
            Finding.scan_id == scan_uuid,
            Finding.severity == Severity.MEDIUM,
        ).count()

        low = db.query(Finding).filter(
            Finding.scan_id == scan_uuid,
            Finding.severity == Severity.LOW,
        ).count()

        total = critical + high + medium + low

        # Calculate duration
        scan = db.query(Scan).filter(Scan.id == scan_uuid).first()
        duration_ms = None
        if scan and scan.triggered_at:
            delta = datetime.now(timezone.utc) - (
                scan.triggered_at.replace(tzinfo=timezone.utc)
                if scan.triggered_at.tzinfo is None
                else scan.triggered_at
            )
            duration_ms = int(delta.total_seconds() * 1000)

        # Update scan record
        db.query(Scan).filter(Scan.id == scan_uuid).update({
            "status": ScanStatus.completed,
            "completed_at": datetime.now(timezone.utc),
            "total_findings": total,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "duration_ms": duration_ms,
        })

        # Update repository last_scan_at
        if scan:
            from models.repo import Repository
            db.query(Repository).filter(
                Repository.id == scan.repo_id
            ).update({
                "last_scan_at": datetime.now(timezone.utc),
            })

        db.commit()

        # Run correlation
        try:
            from services.correlation import run_correlation

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                correlations = loop.run_until_complete(
                    _run_async_correlation(scan_id)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.warning("Correlation failed for scan %s: %s", scan_id, e)

        # Enqueue AI tasks
        from workers.tasks.ai_tasks import (
            update_risk_scores_task,
            generate_fixes_task,
        )
        update_risk_scores_task.delay(scan_id)

        if critical > 0 or high > 0:
            generate_fixes_task.delay(scan_id)

        # Check if model retrain is needed
        from config import settings
        from services.ai.risk_model import RiskModel

        try:
            model = RiskModel(settings.ML_MODEL_PATH)
            scans_since = model.increment_scan_count()

            if scans_since >= settings.ML_RETRAIN_EVERY_N_SCANS:
                from workers.tasks.maintenance_tasks import retrain_model_task
                retrain_model_task.delay()
        except Exception as e:
            logger.warning("Failed to check retrain: %s", e)

        # Send alerts for critical findings
        if critical > 0:
            try:
                findings_data = []
                critical_findings = db.query(Finding).filter(
                    Finding.scan_id == scan_uuid,
                    Finding.severity == Severity.CRITICAL,
                ).all()
                for f in critical_findings:
                    findings_data.append({
                        "severity": f.severity.value,
                        "rule_id": f.rule_id,
                        "file_path": f.file_path,
                        "line_number": f.line_number,
                        "message": f.message,
                    })

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    from services.alerts import send_slack_alert
                    loop.run_until_complete(
                        send_slack_alert(findings_data, scan, scan.repository if scan else None)
                    )
                finally:
                    loop.close()
            except Exception as e:
                logger.warning("Failed to send alert: %s", e)

        logger.info(
            "Scan finalized: scan=%s total=%d critical=%d high=%d medium=%d low=%d",
            scan_id, total, critical, high, medium, low,
        )

        return {
            "scan_id": scan_id,
            "total_findings": total,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        }

    except Exception as e:
        db.rollback()
        try:
            from models.scan import Scan, ScanStatus
            db.query(Scan).filter(Scan.id == UUID(scan_id)).update({
                "status": ScanStatus.failed,
                "completed_at": datetime.now(timezone.utc),
            })
            db.commit()
        except Exception:
            db.rollback()

        logger.error("Scan finalization failed: scan=%s error=%s", scan_id, e)
        raise
    finally:
        db.close()


async def _run_async_correlation(scan_id: str) -> int:
    """Helper to run async correlation in sync context."""
    from database import AsyncSessionLocal
    from services.correlation import run_correlation

    async with AsyncSessionLocal() as session:
        return await run_correlation(UUID(scan_id), session)
