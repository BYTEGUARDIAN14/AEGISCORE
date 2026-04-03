"""
AEGISCORE — FixSuggestion model.
AI-generated code fix suggestions from local LLM (Ollama).
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class FixConfidence(str, enum.Enum):
    """Confidence level of an AI-generated fix."""
    high = "high"
    medium = "medium"
    low = "low"


class FixSuggestion(Base):
    """
    An AI-generated code fix for a specific finding.
    Generated locally via Ollama (codellama:7b) with zero data egress.
    Contains unified diff, human-readable explanation, and confidence level.
    """
    __tablename__ = "fix_suggestions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    finding_id = Column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    model_used = Column(String(100), nullable=False)
    unified_diff = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    confidence = Column(
        Enum(FixConfidence, name="fix_confidence_enum"),
        nullable=False,
    )
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    applied = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    finding = relationship("Finding", back_populates="fix_suggestion")

    def __repr__(self) -> str:
        return (
            f"<FixSuggestion finding_id={self.finding_id} "
            f"confidence={self.confidence} applied={self.applied}>"
        )
