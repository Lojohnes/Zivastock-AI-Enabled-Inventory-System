from datetime import date

import pandas as pd

from app.services.feature_engineering_service import FeatureEngineeringService


def test_feature_engineering_is_as_of_date_safe():
    events = pd.DataFrame([
        {"product_id": 1, "event_type": "RECEIPT", "quantity": 100, "unit_cost": 10, "event_timestamp": "2025-12-20T08:00:00Z"},
        {"product_id": 1, "event_type": "SALE", "quantity": 10, "unit_cost": 10, "event_timestamp": "2026-01-01T10:00:00Z"},
        {"product_id": 1, "event_type": "SALE", "quantity": 10, "unit_cost": 10, "event_timestamp": "2026-01-02T10:00:00Z"},
        {"product_id": 1, "event_type": "SALE", "quantity": 999, "unit_cost": 10, "event_timestamp": "2026-01-04T10:00:00Z"},
    ])

    features = FeatureEngineeringService().build_snapshots(
        events,
        as_of_date=date(2026, 1, 2),
        lookback_days=3,
    )

    row = features.iloc[0]
    assert int(row["current_quantity"]) == 80
    assert float(row["daily_sales"]) == 20 / 3
    assert float(row["sales_value"]) == 200
    assert int(row["adjustment_frequency"]) == 0
    assert row["abc_class"] == "A"


def test_feature_engineering_assigns_abc_classes():
    events = pd.DataFrame([
        {"product_id": 1, "event_type": "SALE", "quantity": 100, "unit_cost": 10, "event_timestamp": "2026-01-01T10:00:00Z"},
        {"product_id": 2, "event_type": "SALE", "quantity": 10, "unit_cost": 10, "event_timestamp": "2026-01-01T10:00:00Z"},
        {"product_id": 3, "event_type": "SALE", "quantity": 1, "unit_cost": 10, "event_timestamp": "2026-01-01T10:00:00Z"},
    ])

    features = FeatureEngineeringService().build_snapshots(
        events,
        as_of_date=date(2026, 1, 1),
        lookback_days=1,
    )

    classes = dict(zip(features["product_id"], features["abc_class"]))
    assert classes[1] == "A"
    assert classes[3] == "C"
