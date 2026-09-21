import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_demo_pipeline import run_demo


def package_evidence(output: Path, demo_output: Path, days: int = 60, seed: int = 42) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    demo_summary = run_demo(demo_output, days=days, seed=seed)
    copied = []
    for source in demo_output.iterdir():
        if source.is_file():
            destination = output / source.name
            shutil.copy2(source, destination)
            copied.append({
                "file": destination.name,
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "bytes": destination.stat().st_size,
            })

    package = {
        "package_type": "ZivaStock dissertation validation evidence",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "research_title": "Development and Validation of an Explainable AI-Enabled Inventory Intelligence Framework for Stock Accuracy, Anomaly Detection and Predictive Decision Support in Institutional Retail Environments",
        "objective": "Evaluate whether explainable AI inventory intelligence improves anomaly prioritisation, predictive stockout exposure and management decision support.",
        "dataset": {
            "type": "simulated POS/ERP transaction data",
            "scenario": "abnormal_adjustment",
            "days": days,
            "seed": seed,
            "as_of_date": demo_summary["as_of_date"],
        },
        "models": {
            "anomaly": ["rule_based", "zscore", "isolation_forest"],
            "forecasting": ["naive", "moving_average", "exponential_smoothing"],
            "risk": "transparent weighted component model v1",
        },
        "evaluation_metrics": {
            "anomaly": ["precision", "recall", "f1", "anomaly_rate"],
            "forecasting": ["mae", "rmse", "wape"],
            "recommendations": ["completion_rate", "success_rate", "override_rate"],
        },
        "demo_summary": demo_summary,
        "artifacts": copied,
        "interpretation_rules": [
            "Simulated data is not institutional evidence.",
            "Anomaly detection is not proof of misconduct.",
            "Model performance claims require labelled or confirmed validation data.",
            "Risk weights and thresholds must be calibrated in the research evaluation.",
        ],
        "pending_evidence": [
            "Manual-process baseline timings",
            "Current ZivaStock baseline timings",
            "Formal user evaluation responses",
            "Confirmed anomaly labels or recount outcomes",
            "Institutional-data validation where permissions allow",
        ],
    }
    (output / "validation_package.json").write_text(json.dumps(package, indent=2, default=str), encoding="utf-8")
    return package


def main() -> None:
    parser = argparse.ArgumentParser(description="Package reproducible ZivaStock dissertation validation evidence")
    parser.add_argument("--output", type=Path, default=Path("../reports/validation_package"))
    parser.add_argument("--demo-output", type=Path, default=Path("../reports/demo_phase9"))
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    package = package_evidence(args.output.resolve(), args.demo_output.resolve(), args.days, args.seed)
    print(json.dumps({"output": str(args.output.resolve()), "artifact_count": len(package["artifacts"])}, indent=2))


if __name__ == "__main__":
    main()
