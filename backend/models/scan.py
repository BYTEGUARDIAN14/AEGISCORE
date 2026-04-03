"""
AEGISCORE — Scan and ScanTask models.
Tracks security scan executions and per-scanner task status.
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


class ScanStatus(str, enum.Enum):
    """Status of a scan or scan task."""
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScannerType(str, enum.Enum):
    """Supported security scanners."""
    semgrep = "semgrep"
    bandit = "bandit"
    trivy = "trivy"


class Scan(Base):
    """
    Represents a complete security scan of a repository.
    A scan spawns multiple ScanTasks (one per scanner).
    """
    __tablename__ = "scans"

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
    commit_sha = Column(String(40), nullable=False)
    branch = Column(String(100), nullable=False)
    triggered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        Enum(ScanStatus, name="scan_status_enum"),
        default=ScanStatus.queued,
        nullable=False,
        index=True,
    )
    total_findings = Column(Integer, default=0, nullable=False)
    critical_count = Column(Integer, default=0, nullable=False)
    high_count = Column(Integer, default=0, nullable=False)
    medium_count = Column(Integer, default=0, nullable=False)
    low_count = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Integer, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="scans")
    tasks = relationship(
        "ScanTask",
        back_populates="scan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    findings = relationship(
        "Finding",
        back_populates="scan",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Scan id={self.id} repo_id={self.repo_id} status={self.status}>"


class ScanTask(Base):
    """
    Individual scanner task within a scan.
    One ScanTask per scanner (semgrep, bandit, trivy).
    """
    __tablename__ = "scan_tasks"

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
    scanner = Column(
        Enum(ScannerType, name="scanner_type_enum"),
        nullable=False,
    )
    status = Column(
        Enum(ScanStatus, name="scan_status_enum"),
        default=ScanStatus.queued,
        nullable=False,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    findings_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<ScanTask scanner={self.scanner} status={self.status}>"
