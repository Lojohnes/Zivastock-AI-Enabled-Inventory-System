import json

from scripts.package_validation_evidence import package_evidence


def test_validation_package_contains_research_metadata(tmp_path):
    package = package_evidence(tmp_path / "package", tmp_path / "demo", days=30, seed=42)
    saved = json.loads((tmp_path / "package" / "validation_package.json").read_text(encoding="utf-8"))

    assert package["dataset"]["seed"] == 42
    assert saved["models"]["anomaly"][-1] == "isolation_forest"
    assert "mae" in saved["evaluation_metrics"]["forecasting"]
    assert len(saved["artifacts"]) == 9
