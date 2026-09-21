from datetime import datetime, timezone
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.recommendation import AIRecommendation, RecommendationDecision, RecommendationOutcome


class RecommendationService:
    """Generate explainable recommendations; never mutates inventory automatically."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def generate(self, signals: pd.DataFrame) -> pd.DataFrame:
        required = {"product_id"}
        if not required.issubset(signals.columns):
            raise ValueError("Recommendation signals require product_id")
        rows = []
        for _, row in signals.iterrows():
            product_id = int(row["product_id"])
            location_id = self._optional_int(row.get("location_id"))
            priority = str(row.get("priority", "MONITOR"))
            risk_level = str(row.get("risk_level", "LOW"))
            evidence_strength = self._evidence_strength(row)
            base = {
                "product_id": product_id,
                "location_id": location_id,
                "priority": priority,
                "confidence_score": evidence_strength,
                "feature_date": row.get("feature_date"),
            }

            variance = abs(self._number(row.get("variance_percentage")))
            anomaly = self._number(row.get("anomaly_component", row.get("anomaly_score")))
            adjustments = self._number(row.get("adjustment_frequency"))
            disagreement = self._number(row.get("count_disagreement"))
            stockout_risk = str(row.get("stockout_risk", "LOW"))
            days = row.get("days_until_stockout", row.get("days_of_inventory"))
            days_value = self._number(days, None)
            current = self._number(row.get("current_quantity"))
            demand = self._number(row.get("predicted_daily_demand", row.get("daily_sales")))
            safety = self._number(row.get("safety_stock"))
            excess = self._number(row.get("excess_quantity"))
            slow_moving = bool(self._number(row.get("slow_moving")))
            non_moving = bool(self._number(row.get("non_moving")))

            if anomaly >= 50 or variance >= 5 or adjustments >= 2 or disagreement:
                evidence = self._evidence(row, [
                    (anomaly >= 50, f"Anomaly score is {anomaly:.1f}/100"),
                    (variance >= 5, f"Variance is {variance:.1f}%"),
                    (adjustments >= 2, f"{adjustments:.0f} recent adjustments were recorded"),
                    (bool(disagreement), "Count disagreement indicator is present"),
                ])
                rows.append({
                    **base,
                    "recommendation_type": "TARGETED_RECOUNT",
                    "recommendation_text": "Conduct a targeted recount and review the related movement history.",
                    "evidence": evidence,
                    "expected_impact": {"purpose": "confirm physical quantity and reduce unresolved variance"},
                })

            if anomaly >= 70 or adjustments >= 3:
                evidence = self._evidence(row, [
                    (anomaly >= 70, f"Anomaly score is {anomaly:.1f}/100"),
                    (adjustments >= 3, f"Adjustment frequency is {adjustments:.0f}"),
                ])
                rows.append({
                    **base,
                    "recommendation_type": "INVESTIGATE_ADJUSTMENT",
                    "recommendation_text": "Review recent adjustments, receiving records and movement references.",
                    "evidence": evidence,
                    "expected_impact": {"purpose": "identify the operational cause without assigning blame"},
                })

            if stockout_risk in {"HIGH", "CRITICAL"} or (days_value is not None and days_value <= 5):
                replenish = max(0.0, demand * 7 + safety - current)
                evidence = self._evidence(row, [
                    (True, f"Stockout risk is {stockout_risk}"),
                    (days_value is not None, f"Estimated stock cover is {days_value:.1f} days" if days_value is not None else ""),
                    (demand > 0, f"Predicted daily demand is {demand:.1f} units"),
                ])
                rows.append({
                    **base,
                    "recommendation_type": "REPLENISH",
                    "recommendation_text": f"Review replenishment for approximately {replenish:.1f} units.",
                    "evidence": evidence,
                    "expected_impact": {"estimated_units": round(replenish, 2), "horizon_days": 7},
                })

            if excess > 0 or slow_moving or non_moving:
                evidence = self._evidence(row, [
                    (excess > 0, f"Estimated excess quantity is {excess:.1f} units"),
                    (slow_moving, "Inventory cover indicates slow-moving stock"),
                    (non_moving, "No demand was predicted in the forecast horizon"),
                ])
                rows.append({
                    **base,
                    "recommendation_type": "REDUCE_OR_TRANSFER",
                    "recommendation_text": "Review procurement quantity and consider an internal transfer or controlled reduction.",
                    "evidence": evidence,
                    "expected_impact": {"estimated_excess_units": round(excess, 2)},
                })

            if not any(item["product_id"] == product_id and item.get("feature_date") == row.get("feature_date") for item in rows):
                rows.append({
                    **base,
                    "recommendation_type": "MONITOR",
                    "recommendation_text": "Continue monitoring this product; no immediate intervention signal was identified.",
                    "evidence": ["No configured high-priority signal was triggered"],
                    "expected_impact": {"purpose": "maintain visibility"},
                })
        return pd.DataFrame(rows)

    def persist(self, recommendations: pd.DataFrame, model_version_id: Optional[int] = None) -> int:
        if not self.db:
            raise ValueError("A database session is required")
        for row in recommendations.to_dict("records"):
            self.db.add(AIRecommendation(
                product_id=int(row["product_id"]),
                location_id=self._optional_int(row.get("location_id")),
                recommendation_type=row["recommendation_type"],
                recommendation_text=row["recommendation_text"],
                priority=row["priority"],
                confidence_score=float(row["confidence_score"]) if row.get("confidence_score") is not None else None,
                evidence=row["evidence"],
                expected_impact=row["expected_impact"],
                model_version_id=model_version_id,
                status="PENDING",
            ))
        self.db.commit()
        return len(recommendations)

    def decide(self, recommendation_id: int, decision: str, decided_by: int, reason: Optional[str] = None) -> AIRecommendation:
        if not self.db:
            raise ValueError("A database session is required")
        recommendation = self.db.query(AIRecommendation).filter(AIRecommendation.id == recommendation_id).first()
        if not recommendation:
            raise ValueError("Recommendation not found")
        decision = decision.upper()
        if decision not in {"APPROVED", "REJECTED", "OVERRIDDEN"}:
            raise ValueError("Decision must be APPROVED, REJECTED or OVERRIDDEN")
        if recommendation.status != "PENDING":
            raise ValueError(f"Recommendation must be PENDING (currently {recommendation.status})")
        if decision == "OVERRIDDEN" and not reason:
            raise ValueError("An override requires a reason")
        recommendation.status = decision
        self.db.add(RecommendationDecision(
            recommendation_id=recommendation.id,
            decision=decision,
            decided_by=decided_by,
            decision_reason=reason,
            override_flag=int(decision == "OVERRIDDEN"),
        ))
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    def record_outcome(
        self,
        recommendation_id: int,
        outcome_status: str,
        recorded_by: int,
        actual_action: Optional[str] = None,
        actual_result: Optional[str] = None,
        variance_after_action: Optional[float] = None,
        stockout_avoided: Optional[bool] = None,
    ) -> RecommendationOutcome:
        if not self.db:
            raise ValueError("A database session is required")
        recommendation = self.db.query(AIRecommendation).filter(AIRecommendation.id == recommendation_id).first()
        if not recommendation:
            raise ValueError("Recommendation not found")
        outcome_status = outcome_status.upper()
        if outcome_status not in {"SUCCESS", "PARTIAL", "FAILED", "NOT_APPLICABLE", "PENDING"}:
            raise ValueError("Invalid outcome status")
        outcome = RecommendationOutcome(
            recommendation_id=recommendation_id,
            actual_action=actual_action,
            outcome_status=outcome_status,
            actual_result=actual_result,
            variance_after_action=variance_after_action,
            stockout_avoided=int(stockout_avoided) if stockout_avoided is not None else None,
            recorded_by=recorded_by,
        )
        self.db.add(outcome)
        if outcome_status in {"SUCCESS", "PARTIAL", "FAILED", "NOT_APPLICABLE"}:
            recommendation.status = "COMPLETED"
        self.db.commit()
        self.db.refresh(outcome)
        return outcome

    @staticmethod
    def _evidence(row, conditions) -> list[str]:
        return [text for enabled, text in conditions if enabled and text]

    @staticmethod
    def _evidence_strength(row) -> float:
        signals = 0
        signals += int(RecommendationService._number(row.get("anomaly_component", row.get("anomaly_score"))) >= 50)
        signals += int(abs(RecommendationService._number(row.get("variance_percentage"))) >= 5)
        signals += int(RecommendationService._number(row.get("adjustment_frequency")) >= 2)
        signals += int(str(row.get("stockout_risk", "LOW")) in {"HIGH", "CRITICAL"})
        signals += int(RecommendationService._number(row.get("excess_quantity")) > 0)
        return min(100.0, signals * 20.0)

    @staticmethod
    def _number(value, default=0.0):
        if value is None or pd.isna(value):
            return default
        return float(value)

    @staticmethod
    def _optional_int(value):
        return None if value is None or pd.isna(value) else int(value)
