from datetime import date
from typing import Any, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.ml import AnomalyResult, ModelVersion


class AnomalyDetectionService:
    """Compare transparent baselines with Isolation Forest anomaly detection."""

    NUMERIC_FEATURES = (
        "variance_percentage",
        "historical_variance",
        "adjustment_frequency",
        "count_disagreement",
        "sales_velocity",
        "demand_variability",
        "days_of_inventory",
        "inventory_value",
        "sales_value",
        "current_quantity",
    )

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def detect(
        self,
        features: pd.DataFrame,
        algorithm: str,
        threshold: Optional[float] = None,
        contamination: str | float = "auto",
        random_state: int = 42,
    ) -> pd.DataFrame:
        self._validate_input(features)
        algorithm = algorithm.lower().replace(" ", "_")
        if algorithm in {"rule", "rule_based", "threshold"}:
            return self._rule_based(features, threshold if threshold is not None else 50.0)
        if algorithm in {"zscore", "statistical", "statistical_zscore"}:
            return self._zscore(features, threshold if threshold is not None else 2.5)
        if algorithm in {"isolation_forest", "isolationforest"}:
            return self._isolation_forest(features, threshold if threshold is not None else 70.0, contamination, random_state)
        raise ValueError(f"Unsupported anomaly algorithm: {algorithm}")

    def compare(
        self,
        features: pd.DataFrame,
        threshold_rule: float = 50.0,
        threshold_zscore: float = 2.5,
        threshold_isolation_forest: float = 70.0,
        contamination: str | float = "auto",
        random_state: int = 42,
        labels: Optional[list[int]] = None,
    ) -> dict:
        outputs = {
            "rule_based": self.detect(features, "rule_based", threshold_rule),
            "zscore": self.detect(features, "zscore", threshold_zscore),
            "isolation_forest": self.detect(
                features,
                "isolation_forest",
                threshold_isolation_forest,
                contamination,
                random_state,
            ),
        }
        comparison = {}
        for algorithm, result in outputs.items():
            metrics = {
                "records": len(result),
                "anomaly_count": int(result["anomaly_flag"].sum()),
                "anomaly_rate": float(result["anomaly_flag"].mean()) if len(result) else 0.0,
                "mean_score": float(result["anomaly_score"].mean()) if len(result) else 0.0,
            }
            if labels is not None:
                metrics.update(self._classification_metrics(result["anomaly_flag"].tolist(), labels))
            comparison[algorithm] = metrics
        return {"results": outputs, "metrics": comparison}

    def run_and_persist(
        self,
        features: pd.DataFrame,
        algorithms: list[str],
        dataset_version: Optional[str] = None,
        feature_set_version: Optional[str] = None,
        created_by: Optional[int] = None,
        analysis_key: Optional[str] = None,
    ) -> dict:
        if not self.db:
            raise ValueError("A database session is required to persist anomaly results")
        output = {}
        for algorithm in algorithms:
            normalized = algorithm.lower().replace(" ", "_")
            result = self.detect(features, normalized)
            model_version = ModelVersion(
                model_name="inventory_anomaly_detection",
                algorithm=normalized,
                version="v1",
                dataset_version=dataset_version,
                feature_set_version=feature_set_version,
                features=[column for column in self.NUMERIC_FEATURES if column in features.columns],
                hyperparameters={"random_state": 42} if normalized == "isolation_forest" else {},
                evaluation_metrics={
                    "records": len(result),
                    "anomaly_count": int(result["anomaly_flag"].sum()),
                    "anomaly_rate": float(result["anomaly_flag"].mean()) if len(result) else 0.0,
                },
                status="evaluated",
                created_by=created_by,
            )
            self.db.add(model_version)
            self.db.flush()
            for row in result.to_dict("records"):
                self.db.add(AnomalyResult(
                    analysis_key=analysis_key,
                    product_id=int(row["product_id"]),
                    location_id=self._optional_int(row.get("location_id")),
                    feature_date=self._date_value(row["feature_date"]),
                    model_version_id=model_version.id,
                    algorithm=normalized,
                    anomaly_flag=int(row["anomaly_flag"]),
                    anomaly_score=float(row["anomaly_score"]),
                    risk_level=row["risk_level"],
                    threshold_used=float(row["threshold_used"]),
                    evidence=row["evidence"],
                    feature_contributions=row["feature_contributions"],
                ))
            output[normalized] = result
        self.db.commit()
        return output

    def _rule_based(self, features: pd.DataFrame, threshold: float) -> pd.DataFrame:
        result = features.copy()
        scores = []
        evidence_rows = []
        contribution_rows = []
        for _, row in result.iterrows():
            contributions = {
                "variance_percentage": min(abs(self._number(row.get("variance_percentage"))) / 5 * 35, 35),
                "adjustment_frequency": min(self._number(row.get("adjustment_frequency")) / 3 * 25, 25),
                "low_days_of_inventory": max(0, min((3 - self._number(row.get("days_of_inventory"), 3)) / 3 * 25, 25)),
                "count_disagreement": 15 if self._number(row.get("count_disagreement")) else 0,
            }
            score = min(100.0, sum(contributions.values()))
            evidence = [self._evidence_text(name, value) for name, value in contributions.items() if value > 0]
            scores.append(score)
            evidence_rows.append(evidence)
            contribution_rows.append({name: round(value, 4) for name, value in contributions.items() if value > 0})
        result["anomaly_score"] = scores
        result["anomaly_flag"] = [int(score >= threshold) for score in scores]
        result["threshold_used"] = threshold
        result["evidence"] = evidence_rows
        result["feature_contributions"] = contribution_rows
        result["algorithm"] = "rule_based"
        result["risk_level"] = result["anomaly_score"].map(self._risk_level)
        return result

    def _zscore(self, features: pd.DataFrame, threshold: float) -> pd.DataFrame:
        result = features.copy()
        matrix = self._feature_matrix(features)
        means = matrix.mean(axis=0)
        stds = matrix.std(axis=0, ddof=0).replace(0, 1)
        zscores = (matrix - means) / stds
        max_abs = zscores.abs().max(axis=1)
        result["anomaly_score"] = (max_abs / max(threshold, 1) * 100).clip(0, 100)
        result["anomaly_flag"] = (max_abs >= threshold).astype(int)
        result["threshold_used"] = threshold
        result["evidence"] = [self._zscore_evidence(row, threshold) for _, row in zscores.iterrows()]
        result["feature_contributions"] = [
            {column: round(abs(float(value)), 4) for column, value in row.items() if abs(value) >= threshold}
            for _, row in zscores.iterrows()
        ]
        result["algorithm"] = "zscore"
        result["risk_level"] = result["anomaly_score"].map(self._risk_level)
        return result

    def _isolation_forest(
        self,
        features: pd.DataFrame,
        threshold: float,
        contamination: str | float,
        random_state: int,
    ) -> pd.DataFrame:
        if len(features) < 2:
            raise ValueError("Isolation Forest requires at least two feature records")
        from sklearn.ensemble import IsolationForest

        result = features.copy()
        matrix = self._feature_matrix(features)
        model = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=100)
        labels = model.fit_predict(matrix)
        raw_scores = -model.decision_function(matrix)
        scores = self._minmax(raw_scores)
        importances = getattr(model, "feature_importances_", None)
        contributions = []
        evidence = []
        for row in matrix.itertuples(index=False, name=None):
            deviations = abs((pd.Series(row, index=matrix.columns) - matrix.mean()) / matrix.std(ddof=0).replace(0, 1))
            weighted = deviations * pd.Series(importances, index=matrix.columns)
            weighted = weighted[weighted > 0].sort_values(ascending=False)
            contributions.append({column: round(float(value), 4) for column, value in weighted.head(5).items()})
            evidence.append([self._evidence_text(column, value) for column, value in weighted.head(3).items()])
        result["anomaly_score"] = scores
        result["anomaly_flag"] = (labels == -1).astype(int)
        result["threshold_used"] = threshold
        result["evidence"] = evidence
        result["feature_contributions"] = contributions
        result["algorithm"] = "isolation_forest"
        result["risk_level"] = result["anomaly_score"].map(self._risk_level)
        return result

    def _feature_matrix(self, features: pd.DataFrame) -> pd.DataFrame:
        available = [column for column in self.NUMERIC_FEATURES if column in features.columns]
        if not available:
            raise ValueError("No supported numeric anomaly features were supplied")
        return features[available].apply(pd.to_numeric, errors="coerce").fillna(0)

    @staticmethod
    def _validate_input(features: pd.DataFrame) -> None:
        for column in ("product_id", "feature_date"):
            if column not in features.columns:
                raise ValueError(f"Missing anomaly input column: {column}")

    @staticmethod
    def _minmax(values) -> list[float]:
        values = pd.Series(values, dtype=float)
        minimum, maximum = values.min(), values.max()
        if maximum == minimum:
            return [0.0] * len(values)
        return ((values - minimum) / (maximum - minimum) * 100).round(4).tolist()

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 85:
            return "CRITICAL"
        if score >= 65:
            return "HIGH"
        if score >= 40:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _evidence_text(name: str, value: float) -> str:
        labels = {
            "variance_percentage": "Variance exceeds the configured tolerance",
            "adjustment_frequency": "Frequent manual adjustments detected",
            "low_days_of_inventory": "Projected inventory cover is low",
            "count_disagreement": "Count disagreement indicator is present",
        }
        return labels.get(name, f"{name} contributed an anomaly signal ({value:.2f})")

    def _zscore_evidence(self, row: pd.Series, threshold: float) -> list[str]:
        return [
            f"{column} is {abs(float(value)):.2f} standard deviations from its peer distribution"
            for column, value in row.abs().sort_values(ascending=False).items()
            if abs(value) >= threshold
        ][:5]

    @staticmethod
    def _classification_metrics(predictions: list[int], labels: list[int]) -> dict:
        if len(predictions) != len(labels):
            raise ValueError("labels must have the same length as features")
        tp = sum(pred == actual == 1 for pred, actual in zip(predictions, labels))
        fp = sum(pred == 1 and actual == 0 for pred, actual in zip(predictions, labels))
        fn = sum(pred == 0 and actual == 1 for pred, actual in zip(predictions, labels))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {"precision": precision, "recall": recall, "f1": f1}

    @staticmethod
    def _number(value, default: float = 0.0) -> float:
        if value is None or pd.isna(value):
            return default
        return float(value)

    @staticmethod
    def _optional_int(value):
        return None if value is None or pd.isna(value) else int(value)

    @staticmethod
    def _date_value(value):
        if isinstance(value, date):
            return value
        return pd.Timestamp(value).date()
