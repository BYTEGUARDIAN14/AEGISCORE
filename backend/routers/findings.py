"""
AEGISCORE — Findings Router
List and detail security findings with filtering.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.rbac import get_user_team_ids
from database import get_db
from models.finding import CrossRepoLink, Finding, Severity
from models.fix import FixSuggestion
from models.repo import Repository
from models.scan import Scan
from models.user import User
from schemas.finding import (
    CorrelationLink,
    FindingDetail,
    FindingListResponse,
    FindingSummary,
    FixSummary,
)

router = APIRouter(prefix="/findings", tags=["Findings"])


@router.get("", response_model=FindingListResponse)
async def list_findings(
    repo_id: UUID | None = None,
    scan_id: UUID | None = None,
    severity: str | None = None,
    scanner: str | None = None,
    rule_id: str | None = None,
    has_fix: bool | None = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List security findings with optional filters.
    Each finding includes correlated repos and fix availability.
    """
    user_team_ids = await get_user_team_ids(current_user, db)

    query = (
        select(Finding)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )
    count_query = (
        select(func.count(Finding.id))
        .join(Scan, Finding.scan_id == Scan.id)
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )

    if repo_id is not None:
        query = query.where(Scan.repo_id == repo_id)
        count_query = count_query.where(Scan.repo_id == repo_id)

    if scan_id is not None:
        query = query.where(Finding.scan_id == scan_id)
        count_query = count_query.where(Finding.scan_id == scan_id)

    if severity is not None:
        try:
            sev_enum = Severity(severity.upper())
            query = query.where(Finding.severity == sev_enum)
            count_query = count_query.where(Finding.severity == sev_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity: {severity}",
            )

    if scanner is not None:
        query = query.where(Finding.scanner == scanner)
        count_query = count_query.where(Finding.scanner == scanner)

    if rule_id is not None:
        query = query.where(Finding.rule_id == rule_id)
        count_query = count_query.where(Finding.rule_id == rule_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(
        Finding.severity.asc(),
        Finding.file_path.asc(),
    ).limit(limit).offset(offset)

    result = await db.execute(query)
    findings = result.scalars().all()

    finding_summaries = []
    for f in findings:
        # Check if fix exists
        fix_result = await db.execute(
            select(FixSuggestion.id).where(FixSuggestion.finding_id == f.id)
        )
        fix_exists = fix_result.scalar_one_or_none() is not None

        # Get correlated repos
        corr_result = await db.execute(
            select(CrossRepoLink).where(
                (CrossRepoLink.finding_id_a == f.id) |
                (CrossRepoLink.finding_id_b == f.id)
            )
        )
        correlations = corr_result.scalars().all()

        correlated_repos = []
        for corr in correlations:
            linked_finding_id = (
                corr.finding_id_b if corr.finding_id_a == f.id
                else corr.finding_id_a
            )
            linked_finding_result = await db.execute(
                select(Finding)
                .join(Scan, Finding.scan_id == Scan.id)
                .join(Repository, Scan.repo_id == Repository.id)
                .where(Finding.id == linked_finding_id)
            )
            linked_finding = linked_finding_result.scalar_one_or_none()
            if linked_finding:
                linked_scan_result = await db.execute(
                    select(Scan).where(Scan.id == linked_finding.scan_id)
                )
                linked_scan = linked_scan_result.scalar_one_or_none()
                if linked_scan:
                    repo_result = await db.execute(
                        select(Repository).where(Repository.id == linked_scan.repo_id)
                    )
                    linked_repo = repo_result.scalar_one_or_none()
                    if linked_repo:
                        correlated_repos.append(linked_repo.name)

        if has_fix is not None:
            if has_fix and not fix_exists:
                continue
            if not has_fix and fix_exists:
                continue

        finding_summaries.append(FindingSummary(
            id=f.id,
            scan_id=f.scan_id,
            scanner=f.scanner,
            severity=f.severity.value,
            rule_id=f.rule_id,
            file_path=f.file_path,
            line_number=f.line_number,
            message=f.message,
            cwe=f.cwe,
            has_fix=fix_exists,
            correlated_repos=correlated_repos,
        ))

    return FindingListResponse(
        findings=finding_summaries,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{finding_id}", response_model=FindingDetail)
async def get_finding(
    finding_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full finding detail with fix suggestion and correlations."""
    result = await db.execute(
        select(Finding).where(Finding.id == finding_id)
    )
    finding = result.scalar_one_or_none()
    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Verify access
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
                    detail="Not authorized to view this finding",
                )

    # Get fix
    fix_data = None
    if finding.fix_suggestion:
        fix_data = FixSummary(
            id=finding.fix_suggestion.id,
            model_used=finding.fix_suggestion.model_used,
            unified_diff=finding.fix_suggestion.unified_diff,
            explanation=finding.fix_suggestion.explanation,
            confidence=finding.fix_suggestion.confidence.value,
            generated_at=finding.fix_suggestion.generated_at,
            applied=finding.fix_suggestion.applied,
            applied_at=finding.fix_suggestion.applied_at,
        )

    # Get correlations
    corr_result = await db.execute(
        select(CrossRepoLink).where(
            (CrossRepoLink.finding_id_a == finding.id) |
            (CrossRepoLink.finding_id_b == finding.id)
        )
    )
    correlations_data = []
    for corr in corr_result.scalars().all():
        linked_id = (
            corr.finding_id_b if corr.finding_id_a == finding.id
            else corr.finding_id_a
        )
        linked_result = await db.execute(
            select(Finding)
            .join(Scan, Finding.scan_id == Scan.id)
            .join(Repository, Scan.repo_id == Repository.id)
            .where(Finding.id == linked_id)
        )
        linked_finding = linked_result.scalar_one_or_none()
        if linked_finding:
            linked_scan = await db.execute(
                select(Scan).where(Scan.id == linked_finding.scan_id)
            )
            ls = linked_scan.scalar_one_or_none()
            if ls:
                linked_repo = await db.execute(
                    select(Repository).where(Repository.id == ls.repo_id)
                )
                lr = linked_repo.scalar_one_or_none()
                if lr:
                    correlations_data.append(CorrelationLink(
                        linked_finding_id=linked_id,
                        repo_name=lr.name,
                        file_path=linked_finding.file_path,
                        correlation_type=corr.correlation_type,
                    ))

    return FindingDetail(
        id=finding.id,
        scan_id=finding.scan_id,
        scanner=finding.scanner,
        severity=finding.severity.value,
        rule_id=finding.rule_id,
        file_path=finding.file_path,
        line_number=finding.line_number,
        message=finding.message,
        cwe=finding.cwe,
        metadata=finding.metadata,
        fix=fix_data,
        correlations=correlations_data,
    )
