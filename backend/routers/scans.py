"""
AEGISCORE — Scans Router
Trigger scans, list scans, get scan details and live status.
"""

import uuid as uuid_mod
from datetime import datetime, timezone
from uuid import UUID

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.rbac import get_user_team_ids
from config import settings
from database import get_db
from models.repo import Repository
from models.scan import Scan, ScanStatus, ScanTask, ScannerType
from models.user import User
from schemas.scan import (
    ScanDetail,
    ScanListResponse,
    ScanStatusResponse,
    ScanSummary,
    ScanTaskStatus,
    ScanTriggerRequest,
    ScanTriggerResponse,
)

router = APIRouter(prefix="/scans", tags=["Scans"])


def _get_redis_client():
    """Get a synchronous Redis client for rate limiting."""
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def _check_rate_limit(repo_id: UUID) -> bool:
    """
    Check if scan rate limit is exceeded for a repository.
    Limit: 10 scans per hour per repo.
    Returns True if rate limit exceeded.
    """
    try:
        r = _get_redis_client()
        key = f"aegiscore:scan_rate:{repo_id}"
        current = r.get(key)
        if current is not None and int(current) >= 10:
            return True
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 3600)
        pipe.execute()
        return False
    except redis.RedisError:
        # If Redis is down, allow the scan
        return False


@router.post("/trigger", response_model=ScanTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_scan(
    body: ScanTriggerRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a new security scan for a repository.
    Enqueues scanner tasks via Celery and returns scan ID.
    """
    # Verify repo exists and user has access
    result = await db.execute(
        select(Repository).where(Repository.id == body.repo_id)
    )
    repo = result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    user_team_ids = await get_user_team_ids(current_user, db)
    if repo.team_id not in user_team_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to scan this repository",
        )

    # Check rate limit
    if _check_rate_limit(body.repo_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: maximum 10 scans per hour per repository",
        )

    # Create scan record
    scan = Scan(
        repo_id=body.repo_id,
        commit_sha=body.commit_sha,
        branch=body.branch,
        status=ScanStatus.queued,
    )
    db.add(scan)
    await db.flush()

    # Create scan tasks for each requested scanner
    task_ids = []
    for scanner_name in body.scanners:
        scan_task = ScanTask(
            scan_id=scan.id,
            scanner=ScannerType(scanner_name),
            status=ScanStatus.queued,
        )
        db.add(scan_task)
        await db.flush()
        task_ids.append(scan_task.id)

    await db.commit()

    # Enqueue Celery tasks (import here to avoid circular deps)
    try:
        from workers.tasks.scan_tasks import (
            run_bandit_task,
            run_semgrep_task,
            run_trivy_task,
            finalize_scan_task,
        )
        from celery import chord

        repo_path = f"/tmp/repos/{repo.name}"
        scanner_tasks = []

        task_idx = 0
        for scanner_name in body.scanners:
            task_id = str(task_ids[task_idx])
            scan_id = str(scan.id)

            if scanner_name == "semgrep":
                scanner_tasks.append(
                    run_semgrep_task.s(task_id, scan_id, repo_path, settings.SEMGREP_RULES)
                )
            elif scanner_name == "bandit":
                scanner_tasks.append(
                    run_bandit_task.s(task_id, scan_id, repo_path)
                )
            elif scanner_name == "trivy":
                scanner_tasks.append(
                    run_trivy_task.s(task_id, scan_id, repo_path)
                )
            task_idx += 1

        chord(scanner_tasks)(finalize_scan_task.s(scan_id))
    except ImportError:
        # Celery not available — scan stays queued
        pass

    return ScanTriggerResponse(
        scan_id=scan.id,
        status="queued",
        task_ids=task_ids,
        message=f"Scan queued with {len(body.scanners)} scanner(s)",
    )


@router.get("", response_model=ScanListResponse)
async def list_scans(
    repo_id: UUID | None = None,
    branch: str | None = None,
    scan_status: str | None = None,
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List scans with optional filters and pagination."""
    user_team_ids = await get_user_team_ids(current_user, db)

    query = (
        select(Scan)
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )
    count_query = (
        select(func.count(Scan.id))
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )

    if repo_id is not None:
        query = query.where(Scan.repo_id == repo_id)
        count_query = count_query.where(Scan.repo_id == repo_id)

    if branch is not None:
        query = query.where(Scan.branch == branch)
        count_query = count_query.where(Scan.branch == branch)

    if scan_status is not None:
        try:
            status_enum = ScanStatus(scan_status)
            query = query.where(Scan.status == status_enum)
            count_query = count_query.where(Scan.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {scan_status}",
            )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Scan.triggered_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    scans = result.scalars().all()

    return ScanListResponse(
        scans=[ScanSummary.model_validate(s) for s in scans],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{scan_id}", response_model=ScanDetail)
async def get_scan(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full scan detail with task statuses."""
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    # Verify access
    repo_result = await db.execute(
        select(Repository).where(Repository.id == scan.repo_id)
    )
    repo = repo_result.scalar_one_or_none()
    if repo:
        user_team_ids = await get_user_team_ids(current_user, db)
        if repo.team_id not in user_team_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this scan",
            )

    return ScanDetail.model_validate(scan)


@router.get("/{scan_id}/status", response_model=ScanStatusResponse)
async def get_scan_status(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lightweight scan status endpoint for dashboard polling.
    Returns current status and per-scanner task progress.
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    tasks_result = await db.execute(
        select(ScanTask).where(ScanTask.scan_id == scan_id)
    )
    tasks = tasks_result.scalars().all()

    return ScanStatusResponse(
        scan_id=scan.id,
        status=scan.status.value,
        tasks=[ScanTaskStatus.model_validate(t) for t in tasks],
        total_findings=scan.total_findings,
    )
