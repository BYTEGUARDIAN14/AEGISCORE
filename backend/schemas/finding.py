"""
AEGISCORE — Finding Schemas
Pydantic v2 models for security findings and finding details.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class FindingSummary(BaseModel):
    """Finding in list views."""
    id: UUID
    scan_id: UUID
    scanner: str
    severity: str
    rule_id: str
    file_path: str
    line_number: int
    message: str
    cwe: Optional[str] = None
    has_fix: bool = False
    correlated_repos: List[str] = []

    model_config = {"from_attributes": True}


class FindingDetail(BaseModel):
    """Full finding detail with fix suggestion if exists."""
    id: UUID
    scan_id: UUID
    scanner: str
    severity: str
    rule_id: str
    file_path: str
    line_number: int
    message: str
    cwe: Optional[str] = None
    metadata: Dict[str, Any] = {}
    fix: Optional["FixSummary"] = None
    correlations: List["CorrelationLink"] = []

    model_config = {"from_attributes": True}


class FixSummary(BaseModel):
    """Embedded fix summary within finding detail."""
    id: UUID
    model_used: str
    unified_diff: str
    explanation: str
    confidence: str
    generated_at: datetime
    applied: bool
    applied_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CorrelationLink(BaseModel):
    """Cross-repo correlation within finding detail."""
    linked_finding_id: UUID
    repo_name: str
    file_path: str
    correlation_type: str


class FindingListResponse(BaseModel):
    """Paginated finding list."""
    findings: List[FindingSummary]
    total: int
    limit: int
    offset: int
