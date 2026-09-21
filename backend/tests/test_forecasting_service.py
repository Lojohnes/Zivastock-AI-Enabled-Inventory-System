from datetime import date, datetime, timezone

import pandas as pd

from app.models.product import Product
from app.services.forecasting_service import ForecastingService


def sales_data(days=30):
    rows = []
    for offset in range(days):
        timestamp = datetime(2025, 12, 1 + offset, 12, tzinfo=timezone.utc)
        rows.append({"product_id": 1, "event_type": "SALE", "quantity": 10, "event_timestamp": timestamp})
        rows.append({"product_id": 2, "event_type": "SALE", "quantity": 2, "event_timestamp": timestamp})
    return pd.DataFrame(rows)


def test_forecast_models_are_compared_and_forecast_is_reproducible():
    service = ForecastingService()
    sales = sales_data()
    comparison = service.compare_models(sales, date(2025, 12, 30), validation_horizon=7)
    forecasts, second_comparison = service.forecast(sales, date(2025, 12, 30), horizon_days=7)

    assert set(comparison["model_algorithm"]) == {"naive", "moving_average", "exponential_smoothing"}
    assert {"mae", "rmse", "wape"}.issubset(comparison.columns)
    assert len(forecasts) == 14
    assert forecasts["predicted_demand"].ge(0).all()
    assert comparison.equals(second_comparison)


def test_stockout_and_overstock_exposure_is_transparent():
    service = ForecastingService()
    forecasts = pd.DataFrame([
        {"product_id": 1, "location_id": None, "predicted_demand": 10, "model_algorithm": "moving_average"},
        {"product_id": 2, "location_id": None, "predicted_demand": 0, "model_algorithm": "moving_average"},
    ])
    inventory = pd.DataFrame([
        {"product_id": 1, "location_id": None, "current_quantity": 15},
        {"product_id": 2, "location_id": None, "current_quantity": 100},
    ])

    exposure = service.exposure(forecasts, inventory, date(2026, 1, 1), safety_stock=5)
    urgent = exposure.loc[exposure["product_id"] == 1].iloc[0]
    excess = exposure.loc[exposure["product_id"] == 2].iloc[0]

    assert urgent["days_until_stockout"] == 1
    assert urgent["stockout_risk"] == "CRITICAL"
    assert excess["non_moving"] == 1
    assert excess["excess_quantity"] == 100


def test_scenario_analysis_changes_stockout_exposure():
    service = ForecastingService()
    normal = service.scenario_analysis(200, 20, horizon_days=7)
    high_demand = service.scenario_analysis(200, 20, horizon_days=7, demand_change_pct=20)
    delayed = service.scenario_analysis(200, 20, horizon_days=7, supplier_delay_days=2)

    assert high_demand["adjusted_daily_demand"] == 24
    assert high_demand["days_until_stockout"] < normal["days_until_stockout"]
    assert delayed["ending_quantity_after_horizon"] < normal["ending_quantity_after_horizon"]


def test_forecast_and_exposure_can_be_persisted(db_session):
    db_session.add_all([
        Product(id=1, barcode="F-001", product_code="F001", description="Forecast One", unit_of_measure="EA", system_quantity=100, unit_cost=1),
        Product(id=2, barcode="F-002", product_code="F002", description="Forecast Two", unit_of_measure="EA", system_quantity=100, unit_cost=1),
    ])
    db_session.commit()
    service = ForecastingService(db_session)
    forecasts, _ = service.forecast(sales_data(), date(2025, 12, 30), horizon_days=3)
    assert service.persist_forecasts(forecasts) == len(forecasts)
    exposure = service.exposure(
        forecasts,
        pd.DataFrame([{"product_id": 1, "current_quantity": 100}, {"product_id": 2, "current_quantity": 100}]),
        date(2026, 1, 1),
    )
    assert service.persist_exposure(exposure) == 2
