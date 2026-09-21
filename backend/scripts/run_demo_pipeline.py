import argparse
import hashlib
import json
import os
import sys
from datetime import date, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if os.environ.get("DEBUG", "").lower() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
    os.environ["DEBUG"] = "True"

from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.forecasting_service import ForecastingService
from app.services.recommendation_service import RecommendationService
from app.services.risk_scoring_service import InventoryRiskService
from app.services.transaction_simulator import TransactionSimulator


def run_demo(output: Path, days: int = 60, seed: int = 42) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    start = date(2026, 1, 1)
    as_of = start + timedelta(days=days - 1)
    transactions = TransactionSimulator(seed=seed).generate(
        days=days,
        scenario="abnormal_adjustment",
    )
    barcode_ids = {barcode: index + 1 for index, barcode in enumerate(sorted(transactions["barcode"].unique()))}
    transactions["product_id"] = transactions["barcode"].map(barcode_ids)
    transactions["event_timestamp"] = pd.to_datetime(transactions["event_timestamp"], utc=True)

    features = FeatureEngineeringService().build_snapshots(transactions, as_of, lookback_days=30)
    anomaly_service = AnomalyDetectionService()
    anomaly_comparison = anomaly_service.compare(features)
    anomaly = anomaly_comparison["results"]["isolation_forest"]
    risk = InventoryRiskService().calculate(features, anomaly)

    forecasting = ForecastingService()
    forecasts, forecast_comparison = forecasting.forecast(
        transactions,
        as_of,
        horizon_days=7,
        validation_horizon=7,
    )
    inventory = features[["product_id", "location_id", "current_quantity"]].copy()
    exposure = forecasting.exposure(forecasts, inventory, as_of)
    combined = risk.merge(
        exposure[[
            "product_id", "location_id", "predicted_daily_demand", "safety_stock",
            "days_until_stockout", "stockout_risk", "excess_quantity", "slow_moving", "non_moving",
        ]],
        on=["product_id", "location_id"],
        how="left",
    )
    recommendations = RecommendationService().generate(combined)

    files = {
        "transactions": transactions,
        "features": features,
        "anomaly_results": anomaly,
        "forecast_comparison": forecast_comparison,
        "forecasts": forecasts,
        "exposure": exposure,
        "risk_scores": risk,
        "recommendations": recommendations,
    }
    artifact_manifest = {}
    for name, frame in files.items():
        path = output / f"{name}.csv"
        frame.to_csv(path, index=False)
        artifact_manifest[name] = {
            "path": str(path),
            "records": len(frame),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    summary = {
        "scenario": "abnormal_adjustment",
        "seed": seed,
        "days": days,
        "as_of_date": as_of.isoformat(),
        "product_count": len(barcode_ids),
        "transaction_count": len(transactions),
        "feature_count": len(features),
        "anomaly_count": int(anomaly["anomaly_flag"].sum()),
        "critical_or_high_risk_count": int(risk["risk_level"].isin(["CRITICAL", "HIGH"]).sum()),
        "stockout_risk_count": int(exposure["stockout_risk"].isin(["CRITICAL", "HIGH"]).sum()),
        "recommendation_count": len(recommendations),
        "artifacts": artifact_manifest,
        "validation_notes": [
            "All records in this run are simulated and are not institutional data.",
            "Isolation Forest output is used for the demonstration anomaly result.",
            "Forecast metrics are produced from a time-ordered holdout period.",
            "Risk and recommendation outputs are generated from the preceding pipeline artifacts.",
        ],
    }
    (output / "validation_evidence.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a reproducible ZivaStock end-to-end demonstration pipeline")
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("../reports/demo_phase9"))
    args = parser.parse_args()
    if args.days < 30:
        raise SystemExit("The demonstration requires at least 30 days for validation and feature windows")
    summary = run_demo(args.output.resolve(), args.days, args.seed)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
