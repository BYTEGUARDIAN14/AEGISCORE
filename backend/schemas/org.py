"""
AEGISCORE — Organization Schemas
Pydantic v2 models for organizations, teams, and memberships.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class OrgCreate(BaseModel):
    """Request body for POST /orgs."""
    name: str
    slug: str
    plan: str = "free"

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug must contain only alphanumeric characters, hyphens, and underscores")
        return v


class OrgResponse(BaseModel):
    """Organization detail response."""
    id: UUID
    name: str
    slug: str
    created_at: datetime
    plan: str
    scan_count: int

    model_config = {"from_attributes": True}


class TeamCreate(BaseModel):
    """Request body for POST /orgs/{org_id}/teams."""
    name: str
    slug: str

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug must contain only alphanumeric characters, hyphens, and underscores")
        return v


class TeamResponse(BaseModel):
    """Team detail response."""
    id: UUID
    org_id: UUID
    name: str
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberAdd(BaseModel):
    """Request body for adding a team member."""
    user_id: UUID
    role: str = "developer"

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        allowed = {"developer", "security_lead", "admin"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return v


class MemberResponse(BaseModel):
    """Team membership response."""
    id: UUID
    team_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class OrgDetailResponse(BaseModel):
    """Organization detail with teams."""
    id: UUID
    name: str
    slug: str
    created_at: datetime
    plan: str
    scan_count: int
    teams: List[TeamResponse] = []

    model_config = {"from_attributes": True}
