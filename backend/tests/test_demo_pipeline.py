import json

from scripts.run_demo_pipeline import run_demo


def test_demo_pipeline_writes_reproducible_validation_artifacts(tmp_path):
    summary = run_demo(tmp_path, days=30, seed=42)

    assert summary["transaction_count"] > 0
    assert summary["feature_count"] == 5
    assert summary["recommendation_count"] > 0
    assert (tmp_path / "validation_evidence.json").exists()
    for artifact in summary["artifacts"].values():
        assert artifact["records"] > 0
        assert len(artifact["sha256"]) == 64

    persisted = json.loads((tmp_path / "validation_evidence.json").read_text(encoding="utf-8"))
    assert persisted["seed"] == 42
    assert persisted["scenario"] == "abnormal_adjustment"
