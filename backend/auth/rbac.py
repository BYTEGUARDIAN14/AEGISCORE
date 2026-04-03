"""
AEGISCORE — Role-Based Access Control
RBAC utilities for org-level and team-level permission checks.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.org import Organization, Team, TeamMembership, MemberRole
from models.user import User


async def check_org_membership(
    user: User,
    org_id: UUID,
    db: AsyncSession,
) -> list[TeamMembership]:
    """
    Verify that a user belongs to at least one team in the organization.

    Args:
        user: Current authenticated user.
        org_id: Organization UUID to check.
        db: Database session.

    Returns:
        List of user's team memberships in this org.

    Raises:
        HTTPException 403: If user is not a member of the organization.
    """
    result = await db.execute(
        select(TeamMembership)
        .join(Team, TeamMembership.team_id == Team.id)
        .where(
            Team.org_id == org_id,
            TeamMembership.user_id == user.id,
        )
    )
    memberships = result.scalars().all()

    if not memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    return list(memberships)


async def check_team_membership(
    user: User,
    team_id: UUID,
    db: AsyncSession,
    required_roles: list[MemberRole] | None = None,
) -> TeamMembership:
    """
    Verify that a user belongs to a specific team, optionally with a required role.

    Args:
        user: Current authenticated user.
        team_id: Team UUID to check.
        db: Database session.
        required_roles: If set, user must hold one of these roles.

    Returns:
        The user's TeamMembership for this team.

    Raises:
        HTTPException 403: If user is not a member or lacks required role.
    """
    result = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == user.id,
        )
    )
    membership = result.scalar_one_or_none()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team",
        )

    if required_roles and membership.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient role. Required: {', '.join(r.value for r in required_roles)}",
        )

    return membership


async def check_org_admin(
    user: User,
    org_id: UUID,
    db: AsyncSession,
) -> TeamMembership:
    """
    Check if a user is an admin in any team of the organization.

    Raises:
        HTTPException 403: If user is not an admin.
    """
    memberships = await check_org_membership(user, org_id, db)

    admin_membership = next(
        (m for m in memberships if m.role == MemberRole.admin),
        None,
    )

    if admin_membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this operation",
        )

    return admin_membership


async def get_user_team_ids(
    user: User,
    db: AsyncSession,
    org_id: UUID | None = None,
) -> list[UUID]:
    """
    Get all team IDs the user belongs to, optionally filtered by org.

    Args:
        user: Current authenticated user.
        db: Database session.
        org_id: Optional org filter.

    Returns:
        List of team UUIDs.
    """
    query = select(TeamMembership.team_id).where(
        TeamMembership.user_id == user.id
    )

    if org_id is not None:
        query = query.join(Team, TeamMembership.team_id == Team.id).where(
            Team.org_id == org_id
        )

    result = await db.execute(query)
    return [row[0] for row in result.all()]


async def get_user_org_ids(
    user: User,
    db: AsyncSession,
) -> list[UUID]:
    """
    Get all organization IDs the user has access to.

    Returns:
        List of organization UUIDs.
    """
    result = await db.execute(
        select(Team.org_id)
        .join(TeamMembership, TeamMembership.team_id == Team.id)
        .where(TeamMembership.user_id == user.id)
        .distinct()
    )
    return [row[0] for row in result.all()]
