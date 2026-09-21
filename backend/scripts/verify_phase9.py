import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
if os.environ.get("DEBUG", "").lower() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
    os.environ["DEBUG"] = "True"


def verify() -> dict:
    from app.main import app

    paths = set(app.openapi()["paths"])
    required_paths = {
        "/api/v1/inventory-events/ingest",
        "/api/v1/inventory-events/quality",
        "/api/v1/anomalies/detect",
        "/api/v1/anomalies/compare",
        "/api/v1/anomalies/models",
        "/api/v1/risk/command-centre",
        "/api/v1/forecast/run",
        "/api/v1/forecast/scenario",
        "/api/v1/recommendations/generate",
        "/api/v1/recommendations/outcomes/summary",
    }
    checks = {
        "required_api_paths": {
            "passed": required_paths.issubset(paths),
            "missing": sorted(required_paths - paths),
        },
        "migration_head_file": {
            "passed": (BACKEND / "alembic" / "versions" / "010_recommendations.py").exists(),
        },
        "demo_runner": {
            "passed": (BACKEND / "scripts" / "run_demo_pipeline.py").exists(),
        },
        "phase_docs": {
            "passed": (ROOT / "ZivaDocs" / "10_PHASE_8_MODEL_LABORATORY.md").exists(),
        },
    }
    checks["overall"] = {"passed": all(check["passed"] for check in checks.values())}
    return checks


def main() -> None:
    result = verify()
    print(json.dumps(result, indent=2))
    if not result["overall"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
