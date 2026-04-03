"""
AEGISCORE — Repositories Router
Connect, list, update, and disconnect repositories.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.rbac import check_team_membership, get_user_team_ids
from database import get_db
from models.org import MemberRole, Team
from models.repo import Repository
from models.scan import Scan
from models.user import User

router = APIRouter(prefix="/repos", tags=["Repositories"])


class RepoCreate:
    """Not a Pydantic model — using manual validation for clarity."""
    pass


from pydantic import BaseModel


class RepoCreateBody(BaseModel):
    team_id: UUID
    name: str
    github_url: str
    default_branch: str = "main"


class RepoUpdateBody(BaseModel):
    name: str | None = None
    github_url: str | None = None
    default_branch: str | None = None
    is_active: bool | None = None


class RepoResponse(BaseModel):
    id: UUID
    team_id: UUID
    name: str
    github_url: str
    default_branch: str
    connected_at: str
    is_active: bool
    last_scan_at: str | None = None
    last_scan_status: str | None = None
    last_scan_findings: int | None = None

    model_config = {"from_attributes": True}


@router.post("", status_code=status.HTTP_201_CREATED)
async def connect_repository(
    body: RepoCreateBody,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect a new repository to a team."""
    await check_team_membership(
        current_user, body.team_id, db,
        required_roles=[MemberRole.admin, MemberRole.security_lead],
    )

    repo = Repository(
        team_id=body.team_id,
        name=body.name,
        github_url=body.github_url,
        default_branch=body.default_branch,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    return {
        "id": str(repo.id),
        "team_id": str(repo.team_id),
        "name": repo.name,
        "github_url": repo.github_url,
        "default_branch": repo.default_branch,
        "connected_at": repo.connected_at.isoformat(),
        "is_active": repo.is_active,
    }


@router.get("")
async def list_repositories(
    team_id: UUID | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List repositories filtered by user's team memberships."""
    user_team_ids = await get_user_team_ids(current_user, db)

    if not user_team_ids:
        return []

    query = select(Repository).where(
        Repository.team_id.in_(user_team_ids),
        Repository.is_active == True,
    )

    if team_id is not None:
        if team_id not in user_team_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this team",
            )
        query = query.where(Repository.team_id == team_id)

    query = query.order_by(Repository.name)
    result = await db.execute(query)
    repos = result.scalars().all()

    response = []
    for repo in repos:
        repo_data = {
            "id": str(repo.id),
            "team_id": str(repo.team_id),
            "name": repo.name,
            "github_url": repo.github_url,
            "default_branch": repo.default_branch,
            "connected_at": repo.connected_at.isoformat(),
            "is_active": repo.is_active,
            "last_scan_at": repo.last_scan_at.isoformat() if repo.last_scan_at else None,
        }
        response.append(repo_data)

    return response


@router.get("/{repo_id}")
async def get_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get repository detail with last scan summary."""
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id)
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
            detail="Not authorized to access this repository",
        )

    # Get last scan summary
    scan_result = await db.execute(
        select(Scan)
        .where(Scan.repo_id == repo_id)
        .order_by(Scan.triggered_at.desc())
        .limit(1)
    )
    last_scan = scan_result.scalar_one_or_none()

    response = {
        "id": str(repo.id),
        "team_id": str(repo.team_id),
        "name": repo.name,
        "github_url": repo.github_url,
        "default_branch": repo.default_branch,
        "connected_at": repo.connected_at.isoformat(),
        "is_active": repo.is_active,
        "last_scan_at": repo.last_scan_at.isoformat() if repo.last_scan_at else None,
        "last_scan": None,
    }

    if last_scan:
        response["last_scan"] = {
            "id": str(last_scan.id),
            "status": last_scan.status.value,
            "total_findings": last_scan.total_findings,
            "critical_count": last_scan.critical_count,
            "high_count": last_scan.high_count,
            "medium_count": last_scan.medium_count,
            "low_count": last_scan.low_count,
            "triggered_at": last_scan.triggered_at.isoformat(),
            "completed_at": last_scan.completed_at.isoformat() if last_scan.completed_at else None,
        }

    return response


@router.put("/{repo_id}")
async def update_repository(
    repo_id: UUID,
    body: RepoUpdateBody,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update repository settings."""
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id)
    )
    repo = result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    await check_team_membership(
        current_user, repo.team_id, db,
        required_roles=[MemberRole.admin, MemberRole.security_lead],
    )

    if body.name is not None:
        repo.name = body.name
    if body.github_url is not None:
        repo.github_url = body.github_url
    if body.default_branch is not None:
        repo.default_branch = body.default_branch
    if body.is_active is not None:
        repo.is_active = body.is_active

    await db.commit()
    await db.refresh(repo)

    return {
        "id": str(repo.id),
        "team_id": str(repo.team_id),
        "name": repo.name,
        "github_url": repo.github_url,
        "default_branch": repo.default_branch,
        "is_active": repo.is_active,
    }


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect (soft-delete) a repository."""
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id)
    )
    repo = result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    await check_team_membership(
        current_user, repo.team_id, db,
        required_roles=[MemberRole.admin],
    )

    repo.is_active = False
    await db.commit()
