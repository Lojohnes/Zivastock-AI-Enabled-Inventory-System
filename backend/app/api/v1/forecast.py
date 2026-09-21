import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.schemas.forecast import ExposureRequest, ForecastRequest, ScenarioRequest
from app.services.forecasting_service import ForecastingService

router = APIRouter()


@router.post("/compare")
def compare_forecasts(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    try:
        comparison = ForecastingService(db).compare_models(
            pd.DataFrame(request.sales), request.as_of_date, request.validation_horizon
        )
        return {"comparison": comparison.to_dict("records")}
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run")
def run_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    try:
        service = ForecastingService(db)
        forecasts, comparison = service.forecast(
            pd.DataFrame(request.sales),
            request.as_of_date,
            request.horizon_days,
            request.model,
            request.validation_horizon,
        )
        if request.persist:
            service.persist_forecasts(forecasts)
        return {
            "persisted": request.persist,
            "forecasts": forecasts.to_dict("records"),
            "comparison": comparison.to_dict("records"),
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/exposure")
def calculate_exposure(
    request: ExposureRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    try:
        service = ForecastingService(db)
        exposure = service.exposure(
            pd.DataFrame(request.forecasts),
            pd.DataFrame(request.inventory),
            request.calculation_date,
            request.safety_stock,
            request.target_days,
            request.slow_moving_days,
        )
        if request.persist:
            service.persist_exposure(exposure)
        return {"persisted": request.persist, "exposure": exposure.to_dict("records")}
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/scenario")
def run_forecast_scenario(request: ScenarioRequest, user_id: int = Depends(get_current_user_id)):
    del user_id
    try:
        return ForecastingService().scenario_analysis(**request.model_dump())
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
