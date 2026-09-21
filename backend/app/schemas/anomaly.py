from typing import Any, Optional

from pydantic import BaseModel, Field


class AnomalyDetectionRequest(BaseModel):
    features: list[dict[str, Any]] = Field(..., min_length=1)
    algorithms: list[str] = Field(default_factory=lambda: ["rule_based", "zscore", "isolation_forest"])
    dataset_version: Optional[str] = None
    feature_set_version: Optional[str] = "v1"
    persist: bool = False


class AnomalyComparisonRequest(BaseModel):
    features: list[dict[str, Any]] = Field(..., min_length=1)
    labels: Optional[list[int]] = None
    dataset_version: Optional[str] = None
    feature_set_version: Optional[str] = "v1"
