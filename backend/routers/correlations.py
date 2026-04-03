"""
AEGISCORE — Correlations Router
Cross-repository vulnerability correlation endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.rbac import get_user_team_ids
from database import get_db
from models.finding import CrossRepoLink, Finding
from models.repo import Repository
from models.scan import Scan
from models.user import User

router = APIRouter(prefix="/correlations", tags=["Correlations"])


@router.get("")
async def list_correlations(
    rule_id: str | None = None,
    severity: str | None = None,
    repo_id: UUID | None = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List cross-repo correlation groups.
    Groups findings by rule_id showing which repos share vulnerabilities.
    """
    user_team_ids = await get_user_team_ids(current_user, db)

    # Get all cross-repo links accessible to user
    query = (
        select(CrossRepoLink)
        .join(Finding, CrossRepoLink.finding_id_a == Finding.id)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(Repository, Scan.repo_id == Repository.id)
        .where(Repository.team_id.in_(user_team_ids))
    )

    result = await db.execute(query)
    links = result.scalars().all()

    # Build correlation groups by rule_id
    groups = {}

    for link in links:
        # Load both findings
        finding_a_result = await db.execute(
            select(Finding).where(Finding.id == link.finding_id_a)
        )
        finding_a = finding_a_result.scalar_one_or_none()

        finding_b_result = await db.execute(
            select(Finding).where(Finding.id == link.finding_id_b)
        )
        finding_b = finding_b_result.scalar_one_or_none()

        if not finding_a or not finding_b:
            continue

        group_key = finding_a.rule_id

        # Apply filters
        if rule_id and finding_a.rule_id != rule_id:
            continue
        if severity and finding_a.severity.value != severity.upper():
            continue

        if group_key not in groups:
            groups[group_key] = {
                "rule_id": finding_a.rule_id,
                "severity": finding_a.severity.value,
                "repos": {},
                "total_findings": 0,
            }

        # Add repos
        for finding in [finding_a, finding_b]:
            scan_result = await db.execute(
                select(Scan).where(Scan.id == finding.scan_id)
            )
            scan = scan_result.scalar_one_or_none()
            if not scan:
                continue

            repo_result = await db.execute(
                select(Repository).where(Repository.id == scan.repo_id)
            )
            repo = repo_result.scalar_one_or_none()
            if not repo:
                continue

            if repo_id and repo.id != repo_id:
                continue

            repo_key = str(repo.id)
            if repo_key not in groups[group_key]["repos"]:
                # Get team name
                from models.org import Team
                team_result = await db.execute(
                    select(Team).where(Team.id == repo.team_id)
                )
                team = team_result.scalar_one_or_none()

                groups[group_key]["repos"][repo_key] = {
                    "repo_id": str(repo.id),
                    "repo_name": repo.name,
                    "team_name": team.name if team else "Unknown",
                    "files": [],
                }

            file_entry = {
                "file_path": finding.file_path,
                "line_number": finding.line_number,
                "finding_id": str(finding.id),
            }
            if file_entry not in groups[group_key]["repos"][repo_key]["files"]:
                groups[group_key]["repos"][repo_key]["files"].append(file_entry)
                groups[group_key]["total_findings"] += 1

    # Format response
    correlation_groups = []
    for group_key, group_data in groups.items():
        repos_list = list(group_data["repos"].values())
        if len(repos_list) >= 2:
            correlation_groups.append({
                "rule_id": group_data["rule_id"],
                "severity": group_data["severity"],
                "repos_affected": len(repos_list),
                "total_findings": group_data["total_findings"],
                "repos": repos_list,
            })

    # Sort by number of affected repos descending
    correlation_groups.sort(key=lambda x: x["repos_affected"], reverse=True)

    return {
        "correlations": correlation_groups[:limit],
        "total": len(correlation_groups),
    }
