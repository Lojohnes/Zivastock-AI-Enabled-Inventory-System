from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.risk import InventoryRiskScore


class InventoryRiskService:
    """Calculate transparent, component-level inventory risk scores."""

    WEIGHTS = {
        "anomaly": 0.25,
        "variance": 0.20,
        "financial": 0.15,
        "stockout": 0.20,
        "adjustment": 0.10,
        "accuracy": 0.10,
    }

    def __init__(self, db: Optional[Session] = None, calculation_version: str = "v1"):
        self.db = db
        self.calculation_version = calculation_version

    def calculate(
        self,
        features: pd.DataFrame,
        anomaly_results: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        self._validate_features(features)
        result = features.copy()
        if anomaly_results is not None and not anomaly_results.empty:
            anomaly = anomaly_results[[
                column for column in ("product_id", "location_id", "feature_date", "anomaly_score")
                if column in anomaly_results.columns
            ]].copy()
            keys = [column for column in ("product_id", "location_id", "feature_date") if column in anomaly.columns and column in result.columns]
            if keys:
                anomaly = anomaly.rename(columns={"anomaly_score": "model_anomaly_score"})
                result = result.merge(anomaly, on=keys, how="left")
        if "model_anomaly_score" not in result:
            result["model_anomaly_score"] = 0.0
        result["model_anomaly_score"] = pd.to_numeric(result["model_anomaly_score"], errors="coerce").fillna(0).clip(0, 100)

        result["anomaly_component"] = result["model_anomaly_score"]
        variance_values = self._column(result, "variance_percentage")
        result["variance_component"] = pd.to_numeric(variance_values, errors="coerce").fillna(0).abs().clip(0, 20) / 20 * 100
        result["financial_component"] = self._percentile_score(self._column(result, "inventory_value"))
        days = pd.to_numeric(self._column(result, "days_of_inventory"), errors="coerce").fillna(0)
        result["stockout_component"] = ((1 - days.clip(0, 14) / 14) * 100).clip(0, 100)
        adjustments = pd.to_numeric(self._column(result, "adjustment_frequency"), errors="coerce").fillna(0)
        result["adjustment_component"] = (adjustments.clip(0, 5) / 5 * 100)
        variance = pd.to_numeric(variance_values, errors="coerce").fillna(0).abs()
        disagreement = pd.to_numeric(self._column(result, "count_disagreement"), errors="coerce").fillna(0)
        result["accuracy_component"] = (variance.clip(0, 10) / 10 * 70 + disagreement.clip(0, 1) * 30).clip(0, 100)
        result["criticality_component"] = self._column(result, "abc_class", "C").map({"A": 100, "B": 60, "C": 30}).fillna(30)

        result["total_score"] = sum(
            result[f"{component}_component"] * weight
            for component, weight in self.WEIGHTS.items()
        ).clip(0, 100).round(4)
        result["risk_level"] = result["total_score"].map(self._risk_level)
        result["priority"] = [
            self._priority(risk, abc)
            for risk, abc in zip(result["risk_level"], result.get("abc_class", pd.Series("C", index=result.index)))
        ]
        result["explanation"] = [self._explanation(row) for _, row in result.iterrows()]
        result["calculation_version"] = self.calculation_version
        return result

    def persist(self, scores: pd.DataFrame, analysis_key: Optional[str] = None) -> int:
        if not self.db:
            raise ValueError("A database session is required to persist risk scores")
        count = 0
        for row in scores.to_dict("records"):
            self.db.add(InventoryRiskScore(
                analysis_key=analysis_key,
                product_id=int(row["product_id"]),
                location_id=self._optional_int(row.get("location_id")),
                calculation_date=self._date_value(row["feature_date"]),
                anomaly_score=float(row["anomaly_component"]),
                variance_score=float(row["variance_component"]),
                financial_value_score=float(row["financial_component"]),
                stockout_score=float(row["stockout_component"]),
                adjustment_score=float(row["adjustment_component"]),
                accuracy_score=float(row["accuracy_component"]),
                criticality_score=float(row["criticality_component"]),
                total_score=float(row["total_score"]),
                risk_level=row["risk_level"],
                abc_class=self._optional_text(row.get("abc_class")),
                priority=row["priority"],
                explanation=row["explanation"],
                calculation_version=row["calculation_version"],
            ))
            count += 1
        self.db.commit()
        return count

    def command_centre_summary(self, scores: pd.DataFrame, limit: int = 10) -> dict:
        if scores.empty:
            return {
                "total_products": 0,
                "critical_risks": 0,
                "high_risks": 0,
                "anomalies_requiring_investigation": 0,
                "stockout_risks": 0,
                "abc_breakdown": {"A": 0, "B": 0, "C": 0},
                "top_priorities": [],
            }
        ordered = scores.sort_values(["total_score", "financial_component"], ascending=False)
        top = ordered.head(limit).copy()
        for column in ("location_id", "abc_class"):
            if column not in top:
                top[column] = None
        abc_values = scores["abc_class"] if "abc_class" in scores else pd.Series("C", index=scores.index)
        return {
            "total_products": len(scores),
            "critical_risks": int((scores["risk_level"] == "CRITICAL").sum()),
            "high_risks": int((scores["risk_level"] == "HIGH").sum()),
            "anomalies_requiring_investigation": int((scores["anomaly_component"] >= 50).sum()),
            "stockout_risks": int((scores["stockout_component"] >= 60).sum()),
            "abc_breakdown": {
                abc: int((abc_values == abc).sum())
                for abc in ("A", "B", "C")
            },
            "top_priorities": top[[
                "product_id", "location_id", "feature_date", "total_score", "risk_level", "abc_class", "priority", "explanation"
            ]].to_dict("records"),
        }

    @staticmethod
    def _validate_features(features: pd.DataFrame) -> None:
        for column in ("product_id", "feature_date"):
            if column not in features.columns:
                raise ValueError(f"Missing risk input column: {column}")

    @staticmethod
    def _column(frame: pd.DataFrame, name: str, default=0):
        if name in frame.columns:
            return frame[name]
        return pd.Series(default, index=frame.index)

    @staticmethod
    def _percentile_score(values: pd.Series) -> pd.Series:
        numeric = pd.to_numeric(values, errors="coerce").fillna(0).clip(lower=0)
        if numeric.max() <= 0:
            return pd.Series(0.0, index=numeric.index)
        return numeric.rank(method="average", pct=True) * 100

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 85:
            return "CRITICAL"
        if score >= 70:
            return "HIGH"
        if score >= 45:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _priority(risk: str, abc: str) -> str:
        if risk == "CRITICAL" or (abc == "A" and risk == "HIGH"):
            return "IMMEDIATE"
        if risk == "HIGH" or (abc in {"A", "B"} and risk == "MEDIUM"):
            return "HIGH_PRIORITY"
        if risk == "MEDIUM":
            return "REVIEW"
        return "MONITOR"

    def _explanation(self, row: pd.Series) -> list[str]:
        components = {
            "anomaly": self._number(row.get("anomaly_component")),
            "variance": self._number(row.get("variance_component")),
            "financial exposure": self._number(row.get("financial_component")),
            "stockout exposure": self._number(row.get("stockout_component")),
            "adjustment frequency": self._number(row.get("adjustment_component")),
            "historical accuracy": self._number(row.get("accuracy_component")),
        }
        top = sorted(components.items(), key=lambda item: item[1], reverse=True)
        evidence = [f"{name.title()} contributed {value:.1f}/100 to the component score" for name, value in top if value > 0][:3]
        abc = self._optional_text(row.get("abc_class"))
        if abc:
            evidence.append(f"Product is classified as ABC-{abc}")
        return evidence

    @staticmethod
    def _number(value, default=0.0):
        if value is None or pd.isna(value):
            return default
        return float(value)

    @staticmethod
    def _optional_int(value):
        return None if value is None or pd.isna(value) else int(value)

    @staticmethod
    def _optional_text(value):
        return None if value is None or pd.isna(value) else str(value)

    @staticmethod
    def _date_value(value):
        return value if isinstance(value, date) else pd.Timestamp(value).date()
