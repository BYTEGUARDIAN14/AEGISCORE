"""
AEGISCORE — RiskScore and RiskHistory models.
ML-powered per-file vulnerability risk scoring and trend tracking.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from database import Base


class RiskScore(Base):
    """
    Current ML-predicted risk score for a specific file in a repository.
    Updated after each scan with new feature extraction and model prediction.
    """
    __tablename__ = "risk_scores"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    repo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path = Column(String(1024), nullable=False)
    score = Column(Float, nullable=False)
    calculated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    model_version = Column(String(50), nullable=False)
    feature_snapshot = Column(JSONB, default=dict, nullable=False)

    # Relationships
    repository = relationship("Repository", back_populates="risk_scores")

    def __repr__(self) -> str:
        return f"<RiskScore file={self.file_path!r} score={self.score:.3f}>"


class RiskHistory(Base):
    """
    Historical risk score for a file, recorded after each scan.
    Enables trend analysis and risk trajectory visualization.
    """
    __tablename__ = "risk_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    repo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path = Column(String(1024), nullable=False)
    score = Column(Float, nullable=False)
    scan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    repository = relationship("Repository", back_populates="risk_history")

    def __repr__(self) -> str:
        return f"<RiskHistory file={self.file_path!r} score={self.score:.3f}>"
