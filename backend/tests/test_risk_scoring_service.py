from datetime import date

import pandas as pd

from app.models.product import Product
from app.services.risk_scoring_service import InventoryRiskService


def risk_features():
    return pd.DataFrame([
        {"product_id": 1, "feature_date": date(2026, 1, 1), "variance_percentage": 2, "adjustment_frequency": 0, "days_of_inventory": 20, "inventory_value": 100, "sales_value": 100, "abc_class": "C", "count_disagreement": 0},
        {"product_id": 2, "feature_date": date(2026, 1, 1), "variance_percentage": 30, "adjustment_frequency": 4, "days_of_inventory": 1, "inventory_value": 900, "sales_value": 900, "abc_class": "A", "count_disagreement": 1},
        {"product_id": 3, "feature_date": date(2026, 1, 1), "variance_percentage": 8, "adjustment_frequency": 1, "days_of_inventory": 8, "inventory_value": 300, "sales_value": 300, "abc_class": "B", "count_disagreement": 0},
    ])


def test_risk_score_is_component_based_and_prioritises_critical_product():
    anomaly = pd.DataFrame([
        {"product_id": 1, "feature_date": date(2026, 1, 1), "anomaly_score": 0},
        {"product_id": 2, "feature_date": date(2026, 1, 1), "anomaly_score": 95},
        {"product_id": 3, "feature_date": date(2026, 1, 1), "anomaly_score": 30},
    ])

    scores = InventoryRiskService().calculate(risk_features(), anomaly)
    critical = scores.loc[scores["product_id"] == 2].iloc[0]

    assert critical["total_score"] > 70
    assert critical["risk_level"] in {"HIGH", "CRITICAL"}
    assert critical["priority"] == "IMMEDIATE"
    assert critical["anomaly_component"] == 95
    assert len(critical["explanation"]) > 0


def test_command_centre_summary_ranks_products():
    service = InventoryRiskService()
    scores = service.calculate(risk_features())
    summary = service.command_centre_summary(scores, limit=2)

    assert summary["total_products"] == 3
    assert summary["abc_breakdown"]["A"] == 1
    assert len(summary["top_priorities"]) == 2
    assert summary["top_priorities"][0]["product_id"] == 2


def test_risk_scores_can_be_persisted(db_session):
    db_session.add_all([
        Product(id=1, barcode="RISK-001", product_code="R001", description="Low Risk", unit_of_measure="EA", system_quantity=10, unit_cost=1),
        Product(id=2, barcode="RISK-002", product_code="R002", description="High Risk", unit_of_measure="EA", system_quantity=10, unit_cost=1),
        Product(id=3, barcode="RISK-003", product_code="R003", description="Medium Risk", unit_of_measure="EA", system_quantity=10, unit_cost=1),
    ])
    db_session.commit()

    service = InventoryRiskService(db_session)
    scores = service.calculate(risk_features())
    assert service.persist(scores) == 3
