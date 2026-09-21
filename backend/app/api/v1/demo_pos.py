from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.services.demo_pipeline_service import DemoPipelineService
from app.services.transaction_simulator import TransactionSimulator

router = APIRouter()


@router.post("/run-pipeline")
def run_demo_pipeline(
    scenario: str = Query("abnormal_adjustment"),
    days: int = Query(60, ge=30, le=365),
    seed: int = Query(42),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return DemoPipelineService(db).run(scenario, days, seed, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Demo pipeline failed: {exc}") from exc


@router.get("/generate")
def generate_demo_transactions(
    scenario: str = Query("normal"),
    days: int = Query(30, ge=1, le=365),
    seed: int = Query(42),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del db, user_id
    try:
        frame = TransactionSimulator(seed=seed).generate(days=days, scenario=scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "scenario": scenario,
        "days": days,
        "seed": seed,
        "records": len(frame),
        "transactions": frame.to_dict("records"),
    }
