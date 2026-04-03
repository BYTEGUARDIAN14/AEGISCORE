"""
AEGISCORE — Risk Router
Risk heatmap, history, and ML model status endpoints.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.rbac import get_user_team_ids
from config import settings
from database import get_db
from models.repo import Repository
from models.risk import RiskHistory, RiskScore
from models.scan import Scan
from models.user import User
from schemas.risk import (
    ModelStatusResponse,
    RiskFileScore,
    RiskHeatmapResponse,
    RiskHistoryPoint,
    RiskHistoryResponse,
)

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("/heatmap", response_model=RiskHeatmapResponse)
async def get_risk_heatmap(
    repo_id: UUID,
    min_score: float = 0.0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get risk heatmap for a repository.
    Returns files sorted by risk score descending.
    """
    # Verify access
    repo_result = await db.execute(
        select(Repository).where(Repository.id == repo_id)
    )
    repo = repo_result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    user_team_ids = await get_user_team_ids(current_user, db)
    if repo.team_id not in user_team_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this repository",
        )

    query = (
        select(RiskScore)
        .where(
            RiskScore.repo_id == repo_id,
            RiskScore.score >= min_score,
        )
        .order_by(RiskScore.score.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    scores = result.scalars().all()

    files = []
    for s in scores:
        file_score = RiskFileScore(
            file_path=s.file_path,
            score=s.score,
            calculated_at=s.calculated_at,
            model_version=s.model_version,
            feature_snapshot=s.feature_snapshot,
        )
        files.append(file_score)

    return RiskHeatmapResponse(
        repo_id=str(repo_id),
        files=files,
        total=len(files),
    )


@router.get("/history", response_model=RiskHistoryResponse)
async def get_risk_history(
    repo_id: UUID,
    file_path: str,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get risk score history over time for a specific file.
    """
    # Verify access
    repo_result = await db.execute(
        select(Repository).where(Repository.id == repo_id)
    )
    repo = repo_result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    user_team_ids = await get_user_team_ids(current_user, db)
    if repo.team_id not in user_team_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this repository",
        )

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    query = (
        select(RiskHistory)
        .where(
            RiskHistory.repo_id == repo_id,
            RiskHistory.file_path == file_path,
            RiskHistory.recorded_at >= cutoff,
        )
        .order_by(RiskHistory.recorded_at.asc())
    )

    result = await db.execute(query)
    history = result.scalars().all()

    points = [
        RiskHistoryPoint(
            score=h.score,
            recorded_at=h.recorded_at,
            scan_id=str(h.scan_id) if h.scan_id else None,
        )
        for h in history
    ]

    return RiskHistoryResponse(
        repo_id=str(repo_id),
        file_path=file_path,
        history=points,
    )


@router.get("/model/status", response_model=ModelStatusResponse)
async def get_model_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get ML risk model status including version, accuracy metrics,
    and next retrain countdown.
    """
    try:
        from services.ai.risk_model import RiskModel

        model = RiskModel(settings.ML_MODEL_PATH)

        if model.is_trained():
            metadata = model.get_metadata()
            # Count scans since last training
            total_scans_result = await db.execute(
                select(Scan).order_by(Scan.triggered_at.desc()).limit(1)
            )
            last_scan = total_scans_result.scalar_one_or_none()

            return ModelStatusResponse(
                model_version=metadata.get("model_version", "unknown"),
                last_trained_at=metadata.get("last_trained_at"),
                training_samples=metadata.get("training_samples", 0),
                precision=metadata.get("precision", 0.0),
                recall=metadata.get("recall", 0.0),
                f1_score=metadata.get("f1_score", 0.0),
                is_trained=True,
                next_retrain_in=max(
                    0,
                    settings.ML_RETRAIN_EVERY_N_SCANS
                    - metadata.get("scans_since_train", 0),
                ),
            )
        else:
            return ModelStatusResponse(
                is_trained=False,
                next_retrain_in=settings.ML_RETRAIN_EVERY_N_SCANS,
            )
    except Exception:
        return ModelStatusResponse(
            is_trained=False,
            next_retrain_in=settings.ML_RETRAIN_EVERY_N_SCANS,
        )
