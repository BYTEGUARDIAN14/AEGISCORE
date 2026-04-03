"""
AEGISCORE — AI Celery Tasks
Risk scoring, fix generation, and model retraining tasks.
"""

import logging
import os
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update

from workers.celery_app import celery_app

logger = logging.getLogger("aegiscore.tasks.ai")


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
    name="workers.tasks.ai_tasks.update_risk_scores_task",
    bind=True,
    max_retries=1,
    default_retry_delay=60,
)
def update_risk_scores_task(self, scan_id: str):
    """
    Update ML risk scores for all files changed in this scan.
    Extracts features and runs prediction for each unique file path.
    """
    import asyncio

    db = _get_sync_session()
    try:
        from models.finding import Finding
        from models.risk import RiskHistory, RiskScore
        from models.scan import Scan
        from config import settings
        from services.ai.risk_model import RiskModel

        scan_uuid = UUID(scan_id)

        # Get unique file paths from this scan's findings
        findings = db.query(Finding).filter(Finding.scan_id == scan_uuid).all()
        unique_files = set(f.file_path for f in findings)

        if not unique_files:
            logger.info("No findings to score for scan %s", scan_id)
            return {"files_scored": 0}

        # Get scan details for repo path
        scan = db.query(Scan).filter(Scan.id == scan_uuid).first()
        if not scan:
            logger.warning("Scan %s not found", scan_id)
            return {"files_scored": 0}

        from models.repo import Repository
        repo = db.query(Repository).filter(
            Repository.id == scan.repo_id
        ).first()
        if not repo:
            logger.warning("Repository not found for scan %s", scan_id)
            return {"files_scored": 0}

        repo_path = f"/tmp/repos/{repo.name}"

        # Load risk model
        model = RiskModel(settings.ML_MODEL_PATH)

        files_scored = 0

        for file_path in unique_files:
            try:
                # Extract features
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    features = loop.run_until_complete(
                        _extract_features_async(repo_path, file_path)
                    )
                finally:
                    loop.close()

                # Predict risk score
                score = model.predict(features)
                model_version = (
                    model.get_metadata().get("model_version", "untrained")
                    if model.is_trained()
                    else "untrained"
                )

                # Upsert RiskScore
                existing = db.query(RiskScore).filter(
                    RiskScore.repo_id == scan.repo_id,
                    RiskScore.file_path == file_path,
                ).first()

                if existing:
                    existing.score = score
                    existing.calculated_at = datetime.now(timezone.utc)
                    existing.model_version = model_version
                    existing.feature_snapshot = features
                else:
                    risk_score = RiskScore(
                        repo_id=scan.repo_id,
                        file_path=file_path,
                        score=score,
                        model_version=model_version,
                        feature_snapshot=features,
                    )
                    db.add(risk_score)

                # Insert RiskHistory
                history = RiskHistory(
                    repo_id=scan.repo_id,
                    file_path=file_path,
                    score=score,
                    scan_id=scan_uuid,
                )
                db.add(history)

                files_scored += 1

                # Update Prometheus gauge
                try:
                    from routers.metrics import RISK_SCORE_GAUGE
                    RISK_SCORE_GAUGE.labels(
                        repo=repo.name,
                        file_path=file_path,
                    ).set(score)
                except Exception:
                    pass

            except Exception as e:
                logger.warning(
                    "Failed to score file %s: %s", file_path, e
                )
                continue

        db.commit()

        logger.info(
            "Risk scores updated: scan=%s files=%d", scan_id, files_scored
        )
        return {"files_scored": files_scored}

    except Exception as e:
        db.rollback()
        logger.error(
            "Risk scoring failed: scan=%s error=%s", scan_id, e
        )
        raise
    finally:
        db.close()


@celery_app.task(
    name="workers.tasks.ai_tasks.generate_fixes_task",
    bind=True,
    max_retries=1,
    default_retry_delay=120,
)
def generate_fixes_task(self, scan_id: str):
    """
    Generate AI fix suggestions for CRITICAL and HIGH findings
    that don't already have a fix.
    """
    import asyncio

    db = _get_sync_session()
    try:
        from models.finding import Finding, Severity
        from models.fix import FixConfidence, FixSuggestion
        from models.scan import Scan
        from models.repo import Repository

        scan_uuid = UUID(scan_id)

        # Get critical and high findings without fixes
        findings = (
            db.query(Finding)
            .outerjoin(FixSuggestion, FixSuggestion.finding_id == Finding.id)
            .filter(
                Finding.scan_id == scan_uuid,
                Finding.severity.in_([Severity.CRITICAL, Severity.HIGH]),
                FixSuggestion.id.is_(None),
            )
            .all()
        )

        if not findings:
            logger.info("No findings need fixes for scan %s", scan_id)
            return {"fixes_generated": 0}

        # Get repo path for file reading
        scan = db.query(Scan).filter(Scan.id == scan_uuid).first()
        if not scan:
            return {"fixes_generated": 0}

        repo = db.query(Repository).filter(
            Repository.id == scan.repo_id
        ).first()
        if not repo:
            return {"fixes_generated": 0}

        repo_path = f"/tmp/repos/{repo.name}"
        fixes_generated = 0

        for finding in findings:
            try:
                # Read code context
                code_context = _read_code_context(
                    repo_path, finding.file_path, finding.line_number
                )

                finding_data = {
                    "severity": finding.severity.value,
                    "rule_id": finding.rule_id,
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "message": finding.message,
                    "cwe": finding.cwe,
                }

                # Generate fix via Ollama
                from services.ai.fix_generator import generate_fix

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        generate_fix(finding_data, code_context)
                    )
                finally:
                    loop.close()

                if result is None:
                    continue

                # Insert FixSuggestion
                fix = FixSuggestion(
                    finding_id=finding.id,
                    model_used=result["model_used"],
                    unified_diff=result["unified_diff"],
                    explanation=result["explanation"],
                    confidence=FixConfidence(result["confidence"]),
                )
                db.add(fix)
                db.commit()
                fixes_generated += 1

                logger.info(
                    "Fix generated for finding %s (confidence: %s)",
                    finding.id,
                    result["confidence"],
                )

            except Exception as e:
                db.rollback()
                logger.warning(
                    "Failed to generate fix for finding %s: %s",
                    finding.id,
                    e,
                )
                continue

        logger.info(
            "Fix generation complete: scan=%s generated=%d",
            scan_id,
            fixes_generated,
        )
        return {"fixes_generated": fixes_generated}

    except Exception as e:
        db.rollback()
        logger.error(
            "Fix generation failed: scan=%s error=%s", scan_id, e
        )
        raise
    finally:
        db.close()


def _read_code_context(
    repo_path: str,
    file_path: str,
    line_number: int,
    context_lines: int = 10,
) -> str:
    """
    Read code context around a specific line.
    Returns 10 lines before + flagged line + 10 lines after.
    """
    full_path = os.path.join(repo_path, file_path)

    if not os.path.exists(full_path):
        return f"# File not accessible: {file_path}"

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()

        start = max(0, line_number - context_lines - 1)
        end = min(len(all_lines), line_number + context_lines)

        context_parts = []
        for i in range(start, end):
            line_num = i + 1
            prefix = ">>> " if line_num == line_number else "    "
            context_parts.append(f"{prefix}{line_num:4d} | {all_lines[i].rstrip()}")

        return "\n".join(context_parts)

    except (OSError, UnicodeDecodeError):
        return f"# Unable to read file: {file_path}"


async def _extract_features_async(repo_path: str, file_path: str):
    """Helper to run async feature extraction."""
    from database import AsyncSessionLocal
    from services.ai.feature_extractor import extract_features

    async with AsyncSessionLocal() as session:
        return await extract_features(repo_path, file_path, session)
