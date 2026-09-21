import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.models.ml import ModelVersion
from app.schemas.anomaly import AnomalyComparisonRequest, AnomalyDetectionRequest
from app.services.anomaly_detection_service import AnomalyDetectionService

router = APIRouter()


@router.get("/models")
def list_model_versions(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(100).all()
    return [{
        "id": model.id,
        "model_name": model.model_name,
        "algorithm": model.algorithm,
        "version": model.version,
        "dataset_version": model.dataset_version,
        "feature_set_version": model.feature_set_version,
        "features": model.features,
        "hyperparameters": model.hyperparameters,
        "evaluation_metrics": model.evaluation_metrics,
        "status": model.status,
        "created_at": model.created_at,
    } for model in models]


@router.post("/detect")
def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        features = pd.DataFrame(request.features)
        service = AnomalyDetectionService(db)
        if request.persist:
            outputs = service.run_and_persist(
                features,
                request.algorithms,
                dataset_version=request.dataset_version,
                feature_set_version=request.feature_set_version,
                created_by=user_id,
            )
            return {
                "persisted": True,
                "results": {algorithm: result.to_dict("records") for algorithm, result in outputs.items()},
            }
        return {
            "persisted": False,
            "results": {
                algorithm: service.detect(features, algorithm).to_dict("records")
                for algorithm in request.algorithms
            },
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/compare")
def compare_anomaly_models(
    request: AnomalyComparisonRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    del user_id
    try:
        features = pd.DataFrame(request.features)
        comparison = AnomalyDetectionService(db).compare(features, labels=request.labels)
        return {
            "dataset_version": request.dataset_version,
            "feature_set_version": request.feature_set_version,
            "metrics": comparison["metrics"],
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
