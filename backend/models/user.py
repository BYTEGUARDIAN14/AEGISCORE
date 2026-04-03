"""
AEGISCORE — User model.
Authentication and identity management.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """
    Platform user. Authenticated via email + bcrypt-hashed password.
    Users belong to teams via TeamMembership.
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    email = Column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    memberships = relationship(
        "TeamMembership",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User email={self.email!r} active={self.is_active}>"
