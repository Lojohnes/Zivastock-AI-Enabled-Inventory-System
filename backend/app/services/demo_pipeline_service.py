import pandas as pd
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.product import Product
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.forecasting_service import ForecastingService
from app.services.inventory_event_service import InventoryEventService
from app.services.recommendation_service import RecommendationService
from app.services.risk_scoring_service import InventoryRiskService
from app.services.transaction_simulator import TransactionSimulator


class DemoPipelineService:
    """Load Demo POS data and run the complete AI pipeline for demonstrations."""

    def __init__(self, db: Session):
        self.db = db

    def run(self, scenario: str, days: int, seed: int, user_id: int) -> dict:
        simulator = TransactionSimulator(seed=seed)
        frame = simulator.generate(days=days, scenario=scenario)
        location = self._ensure_location()
        product_ids = self._ensure_products(frame)
        frame["product_id"] = frame["barcode"].map(product_ids)
        frame["location_id"] = location.id
        frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True)

        event_result = InventoryEventService(self.db).ingest_dataframe(
            frame,
            source_system="demo_pos",
        )
        feature_date = frame["event_timestamp"].max().date()
        features = FeatureEngineeringService().build_snapshots(frame, feature_date, lookback_days=min(days, 30))
        anomaly_outputs = AnomalyDetectionService(self.db).run_and_persist(
            features,
            ["rule_based", "zscore", "isolation_forest"],
            dataset_version=f"demo-{scenario}-{seed}",
            feature_set_version="v1",
            created_by=user_id,
        )
        anomaly = anomaly_outputs["isolation_forest"]

        risk_service = InventoryRiskService(self.db)
        risk = risk_service.calculate(features, anomaly)
        risk_count = risk_service.persist(risk)

        forecast_service = ForecastingService(self.db)
        forecasts, comparison = forecast_service.forecast(frame, feature_date, horizon_days=7, validation_horizon=7)
        forecast_count = forecast_service.persist_forecasts(forecasts)
        inventory = features[["product_id", "location_id", "current_quantity"]]
        exposure = forecast_service.exposure(forecasts, inventory, feature_date)
        exposure_count = forecast_service.persist_exposure(exposure)

        combined = risk.merge(
            exposure[[
                "product_id", "location_id", "predicted_daily_demand", "safety_stock",
                "days_until_stockout", "stockout_risk", "excess_quantity", "slow_moving", "non_moving",
            ]],
            on=["product_id", "location_id"],
            how="left",
        )
        recommendations = RecommendationService(self.db).generate(combined)
        recommendation_count = RecommendationService(self.db).persist(recommendations)

        return {
            "scenario": scenario,
            "seed": seed,
            "days": days,
            "feature_date": feature_date,
            "events": event_result,
            "features": len(features),
            "models": list(anomaly_outputs.keys()),
            "anomaly_results": len(anomaly),
            "risk_scores": risk_count,
            "forecast_results": forecast_count,
            "forecast_comparison": comparison.to_dict("records"),
            "exposures": exposure_count,
            "recommendations": recommendation_count,
            "message": "Demo data loaded and AI pipeline completed. Open the AI Command Centre.",
        }

    def _ensure_location(self) -> Location:
        location = self.db.query(Location).filter(Location.name == "Demo POS Store").first()
        if not location:
            location = Location(name="Demo POS Store", type="store", address="Simulated demonstration location")
            self.db.add(location)
            self.db.flush()
        return location

    def _ensure_products(self, frame) -> dict[str, int]:
        product_ids = {}
        for barcode, group in frame.groupby("barcode"):
            product = self.db.query(Product).filter(Product.barcode == barcode).first()
            first = group.iloc[0]
            if not product:
                product = Product(
                    barcode=barcode,
                    product_code=str(first["product_code"]),
                    description=str(first["description"]),
                    unit_of_measure="EA",
                    system_quantity=0,
                    unit_cost=float(first["unit_cost"]),
                    unit_price=float(first["unit_cost"]),
                )
                self.db.add(product)
                self.db.flush()
            product_ids[barcode] = product.id
        self.db.commit()
        return product_ids
