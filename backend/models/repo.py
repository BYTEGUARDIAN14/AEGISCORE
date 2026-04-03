"""
AEGISCORE — Repository model.
Represents a connected Git repository belonging to a team.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Repository(Base):
    """
    A Git repository connected to a team for scanning.
    Tracks connection state, default branch, and last scan time.
    """
    __tablename__ = "repositories"

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
    name = Column(String(255), nullable=False)
    github_url = Column(String(512), nullable=False)
    default_branch = Column(String(100), default="main", nullable=False)
    connected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    team = relationship("Team", back_populates="repositories")
    scans = relationship(
        "Scan",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Scan.triggered_at)",
    )
    risk_scores = relationship(
        "RiskScore",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    risk_history = relationship(
        "RiskHistory",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Repository name={self.name!r} team_id={self.team_id}>"
