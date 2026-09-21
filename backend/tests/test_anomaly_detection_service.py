from datetime import date

import pandas as pd

from app.models.product import Product
from app.services.anomaly_detection_service import AnomalyDetectionService


def anomaly_features():
    return pd.DataFrame([
        {"product_id": 1, "feature_date": date(2026, 1, 1), "variance_percentage": 0, "adjustment_frequency": 0, "days_of_inventory": 14, "sales_velocity": 10, "demand_variability": 1, "inventory_value": 100, "sales_value": 100},
        {"product_id": 2, "feature_date": date(2026, 1, 1), "variance_percentage": 1, "adjustment_frequency": 0, "days_of_inventory": 12, "sales_velocity": 11, "demand_variability": 1, "inventory_value": 110, "sales_value": 110},
        {"product_id": 3, "feature_date": date(2026, 1, 1), "variance_percentage": 2, "adjustment_frequency": 1, "days_of_inventory": 10, "sales_velocity": 9, "demand_variability": 2, "inventory_value": 90, "sales_value": 90},
        {"product_id": 4, "feature_date": date(2026, 1, 1), "variance_percentage": 3, "adjustment_frequency": 0, "days_of_inventory": 9, "sales_velocity": 10, "demand_variability": 1, "inventory_value": 105, "sales_value": 105},
        {"product_id": 5, "feature_date": date(2026, 1, 1), "variance_percentage": 4, "adjustment_frequency": 1, "days_of_inventory": 8, "sales_velocity": 12, "demand_variability": 2, "inventory_value": 120, "sales_value": 120},
        {"product_id": 6, "feature_date": date(2026, 1, 1), "variance_percentage": 80, "adjustment_frequency": 5, "days_of_inventory": 1, "sales_velocity": 60, "demand_variability": 20, "inventory_value": 800, "sales_value": 900},
    ])


def test_all_anomaly_algorithms_return_common_explainable_results():
    service = AnomalyDetectionService()
    features = anomaly_features()

    for algorithm in ("rule_based", "zscore", "isolation_forest"):
        result = service.detect(features, algorithm)
        assert len(result) == len(features)
        assert {"anomaly_flag", "anomaly_score", "risk_level", "evidence", "feature_contributions"}.issubset(result.columns)
        assert result["anomaly_score"].between(0, 100).all()
        assert result["anomaly_flag"].isin([0, 1]).all()


def test_model_comparison_can_calculate_labelled_metrics():
    service = AnomalyDetectionService()
    comparison = service.compare(anomaly_features(), labels=[0, 0, 0, 0, 0, 1])

    assert set(comparison["metrics"]) == {"rule_based", "zscore", "isolation_forest"}
    assert "precision" in comparison["metrics"]["rule_based"]
    assert "f1" in comparison["metrics"]["isolation_forest"]


def test_anomaly_results_and_model_versions_can_be_persisted(db_session):
    product = Product(
        id=1,
        barcode="ANOM-001",
        product_code="A001",
        description="Anomaly Product",
        unit_of_measure="EA",
        system_quantity=100,
        unit_cost=10,
    )
    db_session.add(product)
    db_session.commit()

    outputs = AnomalyDetectionService(db_session).run_and_persist(
        anomaly_features().iloc[[0]],
        ["rule_based"],
        dataset_version="test-v1",
        feature_set_version="v1",
    )

    assert "rule_based" in outputs
    assert db_session.query(Product).count() == 1
