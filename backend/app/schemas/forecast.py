from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    sales: list[dict[str, Any]] = Field(..., min_length=1)
    as_of_date: date
    horizon_days: int = Field(default=7, ge=1, le=365)
    model: Optional[str] = None
    validation_horizon: int = Field(default=7, ge=1, le=90)
    persist: bool = False


class ExposureRequest(BaseModel):
    forecasts: list[dict[str, Any]] = Field(..., min_length=1)
    inventory: list[dict[str, Any]] = Field(..., min_length=1)
    calculation_date: date
    safety_stock: float = Field(default=0, ge=0)
    target_days: int = Field(default=14, ge=1)
    slow_moving_days: int = Field(default=30, ge=1)
    persist: bool = False


class ScenarioRequest(BaseModel):
    current_quantity: float = Field(..., ge=0)
    predicted_daily_demand: float = Field(..., ge=0)
    safety_stock: float = Field(default=0, ge=0)
    horizon_days: int = Field(default=7, ge=1)
    demand_change_pct: float = Field(default=0, ge=-100)
    supplier_delay_days: int = Field(default=0, ge=0)
