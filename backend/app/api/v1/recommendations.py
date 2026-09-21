import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.models.recommendation import AIRecommendation, RecommendationOutcome
from app.core.database import get_db
from app.schemas.recommendation import (
    RecommendationDecisionRequest,
    RecommendationGenerateRequest,
    RecommendationOutcomeRequest,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/outcomes/summary")
def recommendation_outcome_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    total = db.query(AIRecommendation).count()
    pending = db.query(AIRecommendation).filter(AIRecommendation.status == "PENDING").count()
    approved = db.query(AIRecommendation).filter(AIRecommendation.status == "APPROVED").count()
    rejected = db.query(AIRecommendation).filter(AIRecommendation.status == "REJECTED").count()
    overridden = db.query(AIRecommendation).filter(AIRecommendation.status == "OVERRIDDEN").count()
    completed = db.query(AIRecommendation).filter(AIRecommendation.status == "COMPLETED").count()
    success = db.query(RecommendationOutcome).filter(RecommendationOutcome.outcome_status == "SUCCESS").count()
    partial = db.query(RecommendationOutcome).filter(RecommendationOutcome.outcome_status == "PARTIAL").count()
    failed = db.query(RecommendationOutcome).filter(RecommendationOutcome.outcome_status == "FAILED").count()
    return {
        "total_recommendations": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "overridden": overridden,
        "completed": completed,
        "outcomes": {"success": success, "partial": partial, "failed": failed},
        "completion_rate": completed / total * 100 if total else 0,
        "success_rate": success / (success + partial + failed) * 100 if success + partial + failed else 0,
    }


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_recommendations(
    request: RecommendationGenerateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    try:
        service = RecommendationService(db)
        recommendations = service.generate(pd.DataFrame(request.signals))
        if request.persist:
            service.persist(recommendations)
        return {"persisted": request.persist, "recommendations": recommendations.to_dict("records")}
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{recommendation_id}/decision")
def decide_recommendation(
    recommendation_id: int,
    request: RecommendationDecisionRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        recommendation = RecommendationService(db).decide(
            recommendation_id, request.decision, user_id, request.reason
        )
        return recommendation
    except ValueError as exc:
        status_code = 404 if str(exc) == "Recommendation not found" else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.post("/{recommendation_id}/outcome")
def record_recommendation_outcome(
    recommendation_id: int,
    request: RecommendationOutcomeRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        outcome = RecommendationService(db).record_outcome(
            recommendation_id,
            request.outcome_status,
            user_id,
            request.actual_action,
            request.actual_result,
            request.variance_after_action,
            request.stockout_avoided,
        )
        return outcome
    except ValueError as exc:
        status_code = 404 if str(exc) == "Recommendation not found" else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
