"""
AEGISCORE — Fix Schemas
Pydantic v2 models for AI-generated fix suggestions.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class FixResponse(BaseModel):
    """Fix suggestion response."""
    id: UUID
    finding_id: UUID
    model_used: str
    unified_diff: str
    explanation: str
    confidence: str
    generated_at: datetime
    applied: bool
    applied_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FixApplyResponse(BaseModel):
    """Response for POST /fixes/{fix_id}/apply."""
    id: UUID
    finding_id: UUID
    applied: bool
    applied_at: datetime
    message: str


class FixListResponse(BaseModel):
    """Paginated fix list."""
    fixes: List[FixResponse]
    total: int
    limit: int
    offset: int
