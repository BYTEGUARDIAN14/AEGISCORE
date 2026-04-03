"""
AEGISCORE — Authentication Dependencies
FastAPI dependencies for extracting and validating the current user.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import verify_token
from database import get_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts the current user from the JWT token.
    Verifies the token and loads the user from the database.

    Raises:
        HTTPException 401: If the token is invalid or user not found.
    """
    payload = verify_token(token)
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency that ensures the current user is active.

    Raises:
        HTTPException 403: If the user account is deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return current_user


def require_role(roles: list[str]):
    """
    Factory function that creates a dependency to enforce role-based access.

    Args:
        roles: List of allowed roles (e.g., ["admin", "security_lead"]).

    Returns:
        FastAPI dependency function.
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        from models.org import TeamMembership

        result = await db.execute(
            select(TeamMembership).where(
                TeamMembership.user_id == current_user.id
            )
        )
        memberships = result.scalars().all()

        user_roles = {m.role.value for m in memberships}

        if not user_roles.intersection(set(roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(roles)}",
            )
        return current_user

    return role_checker
