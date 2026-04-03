"""
AEGISCORE — Organizations Router
CRUD for organizations, teams, and team memberships.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user, require_role
from auth.rbac import check_org_admin, check_org_membership
from database import get_db
from models.org import MemberRole, Organization, Team, TeamMembership
from models.user import User
from schemas.org import (
    MemberAdd,
    MemberResponse,
    OrgCreate,
    OrgDetailResponse,
    OrgResponse,
    TeamCreate,
    TeamResponse,
)

router = APIRouter(prefix="/orgs", tags=["Organizations"])


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrgCreate,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Create a new organization. Admin only."""
    existing = await db.execute(
        select(Organization).where(Organization.slug == body.slug)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization with slug '{body.slug}' already exists",
        )

    org = Organization(
        name=body.name,
        slug=body.slug,
        plan=body.plan,
    )
    db.add(org)
    await db.flush()

    # Create default team and make creator admin
    default_team = Team(
        org_id=org.id,
        name="Default",
        slug="default",
    )
    db.add(default_team)
    await db.flush()

    membership = TeamMembership(
        team_id=default_team.id,
        user_id=current_user.id,
        role=MemberRole.admin,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(org)

    return org


@router.get("/{org_id}", response_model=OrgDetailResponse)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get organization details."""
    await check_org_membership(current_user, org_id, db)

    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return org


@router.get("/{org_id}/teams", response_model=list[TeamResponse])
async def list_teams(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all teams in an organization."""
    await check_org_membership(current_user, org_id, db)

    result = await db.execute(
        select(Team).where(Team.org_id == org_id).order_by(Team.created_at)
    )
    return result.scalars().all()


@router.post(
    "/{org_id}/teams",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    org_id: UUID,
    body: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new team in an organization."""
    await check_org_admin(current_user, org_id, db)

    existing = await db.execute(
        select(Team).where(
            Team.org_id == org_id,
            Team.slug == body.slug,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team with slug '{body.slug}' already exists in this organization",
        )

    team = Team(
        org_id=org_id,
        name=body.name,
        slug=body.slug,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


@router.post(
    "/{org_id}/teams/{team_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_team_member(
    org_id: UUID,
    team_id: UUID,
    body: MemberAdd,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a member to a team with a specific role."""
    await check_org_admin(current_user, org_id, db)

    # Verify team belongs to org
    team_result = await db.execute(
        select(Team).where(Team.id == team_id, Team.org_id == org_id)
    )
    if team_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found in this organization",
        )

    # Verify user exists
    user_result = await db.execute(
        select(User).where(User.id == body.user_id)
    )
    if user_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check for existing membership
    existing = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == body.user_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this team",
        )

    membership = TeamMembership(
        team_id=team_id,
        user_id=body.user_id,
        role=MemberRole(body.role),
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


@router.delete(
    "/{org_id}/teams/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_team_member(
    org_id: UUID,
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from a team."""
    await check_org_admin(current_user, org_id, db)

    result = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found",
        )

    await db.delete(membership)
    await db.commit()
