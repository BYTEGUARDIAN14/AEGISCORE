"""
AEGISCORE — Risk Schemas
Pydantic v2 models for risk heatmap, history, and model status.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RiskFileScore(BaseModel):
    """Risk score for a single file in the heatmap."""
    file_path: str
    score: float
    calculated_at: datetime
    model_version: str
    feature_snapshot: Dict[str, Any] = {}
    risk_level: str = ""

    model_config = {"from_attributes": True}

    def model_post_init(self, __context: Any) -> None:
        if not self.risk_level:
            if self.score >= 0.8:
                self.risk_level = "CRITICAL"
            elif self.score >= 0.6:
                self.risk_level = "HIGH"
            elif self.score >= 0.4:
                self.risk_level = "MEDIUM"
            else:
                self.risk_level = "MINIMAL"


class RiskHeatmapResponse(BaseModel):
    """Response for GET /risk/heatmap."""
    repo_id: str
    files: List[RiskFileScore]
    total: int


class RiskHistoryPoint(BaseModel):
    """Single point in risk score history."""
    score: float
    recorded_at: datetime
    scan_id: Optional[str] = None

    model_config = {"from_attributes": True}


class RiskHistoryResponse(BaseModel):
    """Response for GET /risk/history."""
    repo_id: str
    file_path: str
    history: List[RiskHistoryPoint]


class ModelStatusResponse(BaseModel):
    """Response for GET /risk/model/status."""
    model_version: Optional[str] = None
    last_trained_at: Optional[datetime] = None
    training_samples: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    is_trained: bool = False
    next_retrain_in: int = 0
