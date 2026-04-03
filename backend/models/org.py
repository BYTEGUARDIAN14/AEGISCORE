"""
AEGISCORE — Organization, Team, and TeamMembership models.
Multi-tenant organizational hierarchy.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class MemberRole(str, enum.Enum):
    """Roles a user can hold within a team."""
    developer = "developer"
    security_lead = "security_lead"
    admin = "admin"


class Organization(Base):
    """
    Top-level tenant. All teams, repos, scans, and findings
    belong to an organization.
    """
    __tablename__ = "organizations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    plan = Column(String(50), default="free", nullable=False)
    scan_count = Column(Integer, default=0, nullable=False)

    # Relationships
    teams = relationship(
        "Team",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Organization name={self.name!r} slug={self.slug!r}>"


class Team(Base):
    """
    A team within an organization. Users are members of teams,
    and repositories are connected to teams.
    """
    __tablename__ = "teams"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    memberships = relationship(
        "TeamMembership",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    repositories = relationship(
        "Repository",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Team name={self.name!r} org_id={self.org_id}>"


class TeamMembership(Base):
    """
    Junction table linking users to teams with a specific role.
    """
    __tablename__ = "team_memberships"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(
        Enum(MemberRole, name="member_role_enum"),
        default=MemberRole.developer,
        nullable=False,
    )
    joined_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    team = relationship("Team", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<TeamMembership team_id={self.team_id} user_id={self.user_id} role={self.role}>"
