from typing import Any, Optional

from pydantic import BaseModel, Field


class RiskScoringRequest(BaseModel):
    features: list[dict[str, Any]] = Field(..., min_length=1)
    anomaly_results: Optional[list[dict[str, Any]]] = None
    calculation_version: str = "v1"
    persist: bool = False


class CommandCentreRequest(RiskScoringRequest):
    limit: int = Field(default=10, ge=1, le=100)
