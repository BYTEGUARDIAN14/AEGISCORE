"""
AEGISCORE — Fixes Router
List AI-generated fix suggestions and apply them.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.rbac import get_user_team_ids
from database import get_db
from models.finding import Finding
from models.fix import FixSuggestion
from models.repo import Repository
from models.scan import Scan
from models.user import User
from schemas.fix import FixApplyResponse, FixListResponse, FixResponse

router = APIRouter(prefix="/fixes", tags=["Fixes"])


@router.get("", response_model=FixListResponse)
async def list_fixes(
    finding_id: UUID | None = None,
    scan_id: UUID | None = None,
    applied: bool | None = None,
    confidence: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List AI-generated fix suggestions with optional filters."""
    user_team_ids = await get_user_team_ids(current_user, db)

    query = (
        select(FixSuggestion)
        .join(Finding, FixSuggestion.finding_id == Finding.id)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )
    count_query = (
        select(func.count(FixSuggestion.id))
        .join(Finding, FixSuggestion.finding_id == Finding.id)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )

    if finding_id is not None:
        query = query.where(FixSuggestion.finding_id == finding_id)
        count_query = count_query.where(FixSuggestion.finding_id == finding_id)

    if scan_id is not None:
        query = query.where(Finding.scan_id == scan_id)
        count_query = count_query.where(Finding.scan_id == scan_id)

    if applied is not None:
        query = query.where(FixSuggestion.applied == applied)
        count_query = count_query.where(FixSuggestion.applied == applied)

    if confidence is not None:
        query = query.where(FixSuggestion.confidence == confidence)
        count_query = count_query.where(FixSuggestion.confidence == confidence)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(FixSuggestion.generated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    fixes = result.scalars().all()

    return FixListResponse(
        fixes=[FixResponse.model_validate(f) for f in fixes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/{fix_id}/apply", response_model=FixApplyResponse)
async def apply_fix(
    fix_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a fix suggestion as applied."""
    result = await db.execute(
        select(FixSuggestion).where(FixSuggestion.id == fix_id)
    )
    fix = result.scalar_one_or_none()
    if fix is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fix suggestion not found",
        )

    # Verify access through finding → scan → repo → team
    finding_result = await db.execute(
        select(Finding).where(Finding.id == fix.finding_id)
    )
    finding = finding_result.scalar_one_or_none()
    if finding:
        scan_result = await db.execute(
            select(Scan).where(Scan.id == finding.scan_id)
        )
        scan = scan_result.scalar_one_or_none()
        if scan:
            repo_result = await db.execute(
                select(Repository).where(Repository.id == scan.repo_id)
            )
            repo = repo_result.scalar_one_or_none()
            if repo:
                user_team_ids = await get_user_team_ids(current_user, db)
                if repo.team_id not in user_team_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authorized to apply this fix",
                    )

    if fix.applied:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fix has already been applied",
        )

    now = datetime.now(timezone.utc)
    fix.applied = True
    fix.applied_at = now

    await db.commit()
    await db.refresh(fix)

    return FixApplyResponse(
        id=fix.id,
        finding_id=fix.finding_id,
        applied=True,
        applied_at=now,
        message="Fix marked as applied successfully",
    )
