from app.services.demo_pipeline_service import DemoPipelineService


def test_demo_pipeline_persists_ai_outputs(db_session):
    result = DemoPipelineService(db_session).run(
        scenario="abnormal_adjustment",
        days=30,
        seed=42,
        user_id=1,
    )

    assert result["features"] == 5
    assert result["anomaly_results"] == 5
    assert result["risk_scores"] == 5
    assert result["exposures"] == 5
    assert result["recommendations"] > 0
