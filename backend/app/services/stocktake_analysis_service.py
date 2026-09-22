from datetime import date, datetime, timezone
from uuid import uuid4

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.models.audit import AuditTrail
from app.models.count import FirstCount, SecondCount
from app.models.product import Product
from app.models.session import StocktakeSession
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.recommendation_service import RecommendationService
from app.services.risk_scoring_service import InventoryRiskService


class StocktakeAnalysisService:
    """Convert completed stocktake counts into Command Centre intelligence."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_session(self, session_id: int, user_id: int) -> dict:
        session = self.db.query(StocktakeSession).filter(StocktakeSession.id == session_id).first()
        if not session:
            raise ValueError("Stocktake session not found")

        first_counts = self.db.query(FirstCount, Product).join(Product, Product.id == FirstCount.product_id).filter(FirstCount.session_id == session_id).all()
        second_counts = self.db.query(SecondCount, Product).join(Product, Product.id == SecondCount.product_id).filter(SecondCount.session_id == session_id).all()
        if not first_counts and not second_counts:
            raise ValueError("No stocktake counts found for this session")

        first_by_product = self._aggregate(first_counts)
        second_by_product = self._aggregate(second_counts)
        product_ids = sorted(set(first_by_product) | set(second_by_product))
        rows = []
        today = date.today()
        for product_id in product_ids:
            source = second_by_product.get(product_id) or first_by_product[product_id]
            first_qty = first_by_product.get(product_id, {}).get("quantity")
            second_qty = second_by_product.get(product_id, {}).get("quantity")
            counted_qty = second_qty if second_qty is not None else source["quantity"]
            system_qty = float(source["system_quantity"])
            variance = float(counted_qty) - system_qty
            variance_pct = variance / abs(system_qty) * 100 if system_qty else (100.0 if variance else 0.0)
            rows.append({
                "product_id": product_id,
                "location_id": session.location_id,
                "feature_date": today,
                "current_quantity": system_qty,
                "average_quantity": system_qty,
                "minimum_quantity": system_qty,
                "maximum_quantity": system_qty,
                "daily_sales": 0.0,
                "weekly_sales": 0.0,
                "sales_velocity": 0.0,
                "demand_variability": 0.0,
                "sales_value": 0.0,
                "inventory_value": system_qty * float(source["unit_cost"]),
                "variance_quantity": variance,
                "variance_percentage": variance_pct,
                "historical_variance": variance,
                "adjustment_frequency": 0,
                "count_disagreement": int(first_qty is not None and second_qty is not None and first_qty != second_qty),
                "days_of_inventory": None,
                "abc_class": "C",
            })

        features = pd.DataFrame(rows)
        analysis_key = f"stocktake-{session_id}-{uuid4().hex}"
        analysis_run = AnalysisRun(
            analysis_key=analysis_key,
            analysis_type="STOCKTAKE",
            reference_id=str(session_id),
            status="RUNNING",
            created_by=user_id,
        )
        self.db.add(analysis_run)
        self.db.flush()
        anomaly_service = AnomalyDetectionService(self.db)
        algorithms = ["rule_based", "zscore"] if len(features) >= 2 else ["rule_based"]
        anomaly_outputs = anomaly_service.run_and_persist(
            features,
            algorithms,
            dataset_version=f"stocktake-session-{session_id}",
            feature_set_version="stocktake-v1",
            created_by=user_id,
            analysis_key=analysis_key,
        )
        anomaly = anomaly_outputs.get("rule_based")
        if anomaly is None:
            anomaly = next(iter(anomaly_outputs.values()))

        risk_service = InventoryRiskService(self.db)
        risks = risk_service.calculate(features, anomaly)
        risk_count = risk_service.persist(risks, analysis_key=analysis_key)
        recommendations = RecommendationService(self.db).generate(risks)
        recommendation_count = RecommendationService(self.db).persist(recommendations, analysis_key=analysis_key)
        analysis_run.status = "COMPLETED"
        analysis_run.completed_at = datetime.now(timezone.utc)
        if "audit_trail" in inspect(self.db.bind).get_table_names():
            self.db.add(AuditTrail(
                user_id=user_id,
                action="INSERT",
                entity_type="AI_ANALYSIS_RUN",
                entity_id=analysis_run.id,
                new_value={"analysis_key": analysis_key, "analysis_type": "STOCKTAKE", "session_id": session_id},
            ))
        self.db.commit()

        return {
            "session_id": session_id,
            "session_name": session.name,
            "counted_products": len(features),
            "anomaly_results": len(anomaly),
            "risk_scores": risk_count,
            "recommendations": recommendation_count,
            "algorithms": list(anomaly_outputs.keys()),
            "message": "Stocktake analysis completed. Open the AI Command Centre to review the latest results.",
        }

    @staticmethod
    def _aggregate(records) -> dict:
        aggregated = {}
        for count, product in records:
            existing = aggregated.get(product.id)
            quantity = float(count.quantity)
            if existing:
                existing["quantity"] += quantity
            else:
                aggregated[product.id] = {
                    "quantity": quantity,
                    "system_quantity": float(product.system_quantity or 0),
                    "unit_cost": float(product.unit_cost or 0),
                }
        return aggregated
