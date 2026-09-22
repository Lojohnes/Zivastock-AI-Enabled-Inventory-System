import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.models.analysis_run import AnalysisRun
from app.models.data_quality import DataQualityBatch
from app.models.forecast import InventoryExposure
from app.models.product import Product
from app.models.recommendation import AIRecommendation
from app.models.risk import InventoryRiskScore
from app.core.database import get_db
from app.schemas.risk import CommandCentreRequest, RiskScoringRequest
from app.services.risk_scoring_service import InventoryRiskService

router = APIRouter()


def _risk_record(score: InventoryRiskScore) -> dict:
    return {
        "id": score.id,
        "product_id": score.product_id,
        "product_name": score.product.description if score.product else None,
        "location_id": score.location_id,
        "calculation_date": score.calculation_date,
        "total_score": float(score.total_score),
        "risk_level": score.risk_level,
        "abc_class": score.abc_class,
        "priority": score.priority,
        "anomaly_score": float(score.anomaly_score),
        "variance_score": float(score.variance_score),
        "financial_value_score": float(score.financial_value_score),
        "stockout_score": float(score.stockout_score),
        "adjustment_score": float(score.adjustment_score),
        "accuracy_score": float(score.accuracy_score),
        "explanation": score.explanation,
    }


def _exposure_record(exposure: InventoryExposure) -> dict:
    return {
        "id": exposure.id,
        "product_id": exposure.product_id,
        "product_name": exposure.product.description if exposure.product else None,
        "location_id": exposure.location_id,
        "calculation_date": exposure.calculation_date,
        "forecast_model": exposure.forecast_model,
        "current_quantity": float(exposure.current_quantity),
        "predicted_daily_demand": float(exposure.predicted_daily_demand),
        "safety_stock": float(exposure.safety_stock),
        "days_until_stockout": float(exposure.days_until_stockout) if exposure.days_until_stockout is not None else None,
        "stockout_date": exposure.stockout_date,
        "stockout_risk": exposure.stockout_risk,
        "excess_quantity": float(exposure.excess_quantity),
        "slow_moving": bool(exposure.slow_moving),
        "non_moving": bool(exposure.non_moving),
        "explanation": exposure.explanation,
    }


@router.get("/command-centre")
def get_command_centre(
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    latest_run = db.query(AnalysisRun).order_by(AnalysisRun.started_at.desc()).first()
    analysis_key = latest_run.analysis_key if latest_run else None
    score_query = db.query(InventoryRiskScore)
    exposure_query = db.query(InventoryExposure)
    recommendation_query = db.query(AIRecommendation).filter(AIRecommendation.status == "PENDING")
    if analysis_key:
        score_query = score_query.filter(InventoryRiskScore.analysis_key == analysis_key)
        exposure_query = exposure_query.filter(InventoryExposure.analysis_key == analysis_key)
        recommendation_query = recommendation_query.filter(AIRecommendation.analysis_key == analysis_key)
    score_rows = score_query.order_by(InventoryRiskScore.created_at.desc()).all()
    latest_scores = {}
    for score in score_rows:
        key = (score.product_id, score.location_id)
        if key not in latest_scores:
            latest_scores[key] = score
    scores = sorted(latest_scores.values(), key=lambda item: float(item.total_score), reverse=True)[:limit]

    exposure_rows = exposure_query.order_by(InventoryExposure.created_at.desc()).all()
    latest_exposures = {}
    for exposure in exposure_rows:
        key = (exposure.product_id, exposure.location_id)
        if key not in latest_exposures:
            latest_exposures[key] = exposure
    exposures = sorted(
        latest_exposures.values(),
        key=lambda item: (item.stockout_risk, float(item.days_until_stockout or 999999)),
    )[:limit]

    recommendation_rows = recommendation_query.order_by(AIRecommendation.created_at.desc()).all()
    latest_recommendations = {}
    for recommendation in recommendation_rows:
        key = (recommendation.product_id, recommendation.recommendation_type)
        if key not in latest_recommendations:
            latest_recommendations[key] = recommendation
    recommendations = list(latest_recommendations.values())[:limit]
    latest_quality = db.query(DataQualityBatch).order_by(DataQualityBatch.created_at.desc()).first()
    return {
        "summary": {
            "total_products": score_query.with_entities(InventoryRiskScore.product_id).distinct().count(),
            "critical_risks": score_query.filter(InventoryRiskScore.risk_level == "CRITICAL").count(),
            "high_risks": score_query.filter(InventoryRiskScore.risk_level == "HIGH").count(),
            "stockout_risks": exposure_query.filter(InventoryExposure.stockout_risk.in_(["HIGH", "CRITICAL"])).count(),
            "excess_inventory": exposure_query.filter(InventoryExposure.excess_quantity > 0).count(),
            "pending_recommendations": recommendation_query.count(),
            "data_quality_score": float(latest_quality.quality_score) if latest_quality else None,
        },
        "top_risks": [_risk_record(score) for score in scores],
        "stockout_exposures": [_exposure_record(exposure) for exposure in exposures],
        "recommendations": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.description if item.product else None,
                "recommendation_type": item.recommendation_type,
                "recommendation_text": item.recommendation_text,
                "priority": item.priority,
                "confidence_score": float(item.confidence_score) if item.confidence_score is not None else None,
                "evidence": item.evidence,
                "expected_impact": item.expected_impact,
                "status": item.status,
            }
            for item in recommendations
        ],
    }


@router.get("/product/{product_id}")
def get_product_intelligence(
    product_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    latest_run = db.query(AnalysisRun).order_by(AnalysisRun.started_at.desc()).first()
    analysis_key = latest_run.analysis_key if latest_run else None
    score_query = db.query(InventoryRiskScore).filter(InventoryRiskScore.product_id == product_id)
    exposure_query = db.query(InventoryExposure).filter(InventoryExposure.product_id == product_id)
    recommendation_query = db.query(AIRecommendation).filter(AIRecommendation.product_id == product_id)
    if analysis_key:
        score_query = score_query.filter(InventoryRiskScore.analysis_key == analysis_key)
        exposure_query = exposure_query.filter(InventoryExposure.analysis_key == analysis_key)
        recommendation_query = recommendation_query.filter(AIRecommendation.analysis_key == analysis_key)
    scores = score_query.order_by(InventoryRiskScore.created_at.desc()).limit(10).all()
    exposures = exposure_query.order_by(InventoryExposure.created_at.desc()).limit(10).all()
    recommendations = recommendation_query.order_by(AIRecommendation.created_at.desc()).limit(20).all()
    return {
        "product": {"id": product.id, "barcode": product.barcode, "description": product.description, "unit_cost": float(product.unit_cost or 0)},
        "risk_scores": [_risk_record(score) for score in scores],
        "exposures": [_exposure_record(exposure) for exposure in exposures],
        "recommendations": [
            {"id": item.id, "recommendation_type": item.recommendation_type, "recommendation_text": item.recommendation_text, "priority": item.priority, "status": item.status, "evidence": item.evidence, "expected_impact": item.expected_impact}
            for item in recommendations
        ],
    }


def _calculate(request, db, user_id):
    del user_id
    features = pd.DataFrame(request.features)
    anomaly = pd.DataFrame(request.anomaly_results) if request.anomaly_results else None
    service = InventoryRiskService(db, request.calculation_version)
    scores = service.calculate(features, anomaly)
    if request.persist:
        service.persist(scores)
    return service, scores


@router.post("/scores")
def calculate_risk_scores(
    request: RiskScoringRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        service, scores = _calculate(request, db, user_id)
        return {
            "persisted": request.persist,
            "scores": scores.to_dict("records"),
            "summary": service.command_centre_summary(scores),
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/command-centre")
def command_centre(
    request: CommandCentreRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        service, scores = _calculate(request, db, user_id)
        return {
            "persisted": request.persist,
            "summary": service.command_centre_summary(scores, request.limit),
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
