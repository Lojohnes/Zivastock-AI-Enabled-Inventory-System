from typing import Any, Optional

from pydantic import BaseModel, Field


class RecommendationGenerateRequest(BaseModel):
    signals: list[dict[str, Any]] = Field(..., min_length=1)
    persist: bool = False


class RecommendationDecisionRequest(BaseModel):
    decision: str
    reason: Optional[str] = None


class RecommendationOutcomeRequest(BaseModel):
    outcome_status: str
    actual_action: Optional[str] = None
    actual_result: Optional[str] = None
    variance_after_action: Optional[float] = None
    stockout_avoided: Optional[bool] = None
