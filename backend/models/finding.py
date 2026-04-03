"""
AEGISCORE — Finding and CrossRepoLink models.
Security findings from scanners and cross-repository correlations.
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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from database import Base


class Severity(str, enum.Enum):
    """Finding severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Finding(Base):
    """
    A single security finding detected by a scanner.
    Contains rule, file location, severity, and optional CWE mapping.
    """
    __tablename__ = "findings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    scan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scanner = Column(String(50), nullable=False, index=True)
    severity = Column(
        Enum(Severity, name="severity_enum"),
        nullable=False,
        index=True,
    )
    rule_id = Column(String(255), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    line_number = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    cwe = Column(String(20), nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    scan = relationship("Scan", back_populates="findings")
    fix_suggestion = relationship(
        "FixSuggestion",
        back_populates="finding",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    correlations_as_a = relationship(
        "CrossRepoLink",
        foreign_keys="CrossRepoLink.finding_id_a",
        back_populates="finding_a",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    correlations_as_b = relationship(
        "CrossRepoLink",
        foreign_keys="CrossRepoLink.finding_id_b",
        back_populates="finding_b",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return (
            f"<Finding severity={self.severity} rule={self.rule_id!r} "
            f"file={self.file_path!r}:{self.line_number}>"
        )


class CrossRepoLink(Base):
    """
    Links two findings from different repositories that share the
    same vulnerability pattern (same rule_id). Used for cross-repo
    correlation analysis.
    """
    __tablename__ = "cross_repo_links"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    finding_id_a = Column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    finding_id_b = Column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    correlation_type = Column(String(100), nullable=False, default="same_rule")
    discovered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    finding_a = relationship(
        "Finding",
        foreign_keys=[finding_id_a],
        back_populates="correlations_as_a",
    )
    finding_b = relationship(
        "Finding",
        foreign_keys=[finding_id_b],
        back_populates="correlations_as_b",
    )

    def __repr__(self) -> str:
        return (
            f"<CrossRepoLink a={self.finding_id_a} b={self.finding_id_b} "
            f"type={self.correlation_type!r}>"
        )
