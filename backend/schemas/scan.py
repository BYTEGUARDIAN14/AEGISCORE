"""
AEGISCORE — Scan Schemas
Pydantic v2 models for scan trigger, status, and listing.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class ScanTriggerRequest(BaseModel):
    """Request body for POST /scans/trigger."""
    repo_id: UUID
    commit_sha: str
    branch: str
    scanners: List[str] = ["semgrep", "bandit", "trivy"]

    @field_validator("commit_sha")
    @classmethod
    def validate_sha(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) != 40 or not all(c in "0123456789abcdef" for c in v):
            raise ValueError("commit_sha must be a 40-character hex string")
        return v

    @field_validator("scanners")
    @classmethod
    def validate_scanners(cls, v: List[str]) -> List[str]:
        allowed = {"semgrep", "bandit", "trivy"}
        for scanner in v:
            if scanner not in allowed:
                raise ValueError(f"Invalid scanner: {scanner}. Allowed: {', '.join(allowed)}")
        if not v:
            raise ValueError("At least one scanner must be specified")
        return v


class ScanTriggerResponse(BaseModel):
    """Response for POST /scans/trigger (202 Accepted)."""
    scan_id: UUID
    status: str
    task_ids: List[UUID]
    message: str


class ScanTaskStatus(BaseModel):
    """Status of an individual scanner task."""
    id: UUID
    scanner: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    findings_count: int = 0
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class ScanSummary(BaseModel):
    """Summary of a scan for list views."""
    id: UUID
    repo_id: UUID
    commit_sha: str
    branch: str
    triggered_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    duration_ms: Optional[int] = None

    model_config = {"from_attributes": True}


class ScanDetail(BaseModel):
    """Detailed scan view with task statuses."""
    id: UUID
    repo_id: UUID
    commit_sha: str
    branch: str
    triggered_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    duration_ms: Optional[int] = None
    tasks: List[ScanTaskStatus] = []

    model_config = {"from_attributes": True}


class ScanStatusResponse(BaseModel):
    """Lightweight status response for polling."""
    scan_id: UUID
    status: str
    tasks: List[ScanTaskStatus] = []
    total_findings: int = 0


class ScanListResponse(BaseModel):
    """Paginated scan list."""
    scans: List[ScanSummary]
    total: int
    limit: int
    offset: int
