from datetime import date

import pandas as pd

from app.models.product import Product
from app.models.recommendation import AIRecommendation
from app.services.recommendation_service import RecommendationService


def recommendation_signals():
    return pd.DataFrame([{
        "product_id": 1,
        "feature_date": date(2026, 1, 1),
        "risk_level": "CRITICAL",
        "priority": "IMMEDIATE",
        "anomaly_component": 90,
        "variance_percentage": 25,
        "adjustment_frequency": 4,
        "count_disagreement": 1,
        "stockout_risk": "CRITICAL",
        "days_until_stockout": 2,
        "current_quantity": 20,
        "predicted_daily_demand": 15,
        "safety_stock": 5,
        "excess_quantity": 0,
        "slow_moving": 0,
        "non_moving": 0,
    }])


def test_generation_creates_explainable_actions():
    recommendations = RecommendationService().generate(recommendation_signals())
    types = set(recommendations["recommendation_type"])

    assert {"TARGETED_RECOUNT", "INVESTIGATE_ADJUSTMENT", "REPLENISH"}.issubset(types)
    assert recommendations["evidence"].map(len).min() > 0
    assert recommendations["confidence_score"].between(0, 100).all()


def test_human_decision_requires_override_reason_and_records_outcome(db_session):
    db_session.add(Product(
        id=1,
        barcode="REC-001",
        product_code="REC001",
        description="Recommendation Product",
        unit_of_measure="EA",
        system_quantity=20,
        unit_cost=5,
    ))
    db_session.commit()
    service = RecommendationService(db_session)
    recommendations = service.generate(recommendation_signals())
    service.persist(recommendations)
    recommendation = db_session.query(AIRecommendation).first()

    try:
        service.decide(recommendation.id, "OVERRIDDEN", 1)
        assert False, "override without reason should fail"
    except ValueError as exc:
        assert "override requires" in str(exc)

    decided = service.decide(recommendation.id, "APPROVED", 1, "Manager reviewed evidence")
    assert decided.status == "APPROVED"
    outcome = service.record_outcome(
        recommendation.id,
        "SUCCESS",
        1,
        actual_action="Targeted recount completed",
        actual_result="Variance confirmed",
    )
    assert outcome.outcome_status == "SUCCESS"
    assert db_session.query(AIRecommendation).get(recommendation.id).status == "COMPLETED"
