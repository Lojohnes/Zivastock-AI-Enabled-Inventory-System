import pandas as pd

from app.services.data_quality_service import DataQualityService


def test_quality_profile_detects_missing_invalid_and_duplicate_rows(db_session):
    dataframe = pd.DataFrame([
        {
            "source_record_id": "Q-001",
            "barcode": "SIM-001",
            "event_type": "SALE",
            "quantity": 2,
            "event_timestamp": "2026-01-01T10:00:00Z",
        },
        {
            "source_record_id": "Q-001",
            "barcode": "SIM-001",
            "event_type": "SALE",
            "quantity": 2,
            "event_timestamp": "2026-01-01T10:00:00Z",
        },
        {
            "source_record_id": "Q-002",
            "barcode": "SIM-001",
            "event_type": "NOT_REAL",
            "quantity": -1,
            "event_timestamp": "not-a-date",
        },
    ])

    assessment = DataQualityService().assess_dataframe(
        dataframe,
        source_system="simulator",
        check_database=False,
    )

    assert assessment["total_records"] == 3
    assert assessment["duplicate_records"] == 1
    assert assessment["invalid_records"] == 1
    assert assessment["quality_score"] == 33.33
    assert assessment["issue_summary"]["duplicate_source_record"] == 1
    assert assessment["issue_summary"]["invalid_event_type"] == 1


def test_quality_profile_can_be_persisted(db_session):
    assessment = DataQualityService().assess_dataframe(
        pd.DataFrame([{
            "source_record_id": "Q-003",
            "barcode": "SIM-001",
            "event_type": "SALE",
            "quantity": 1,
            "event_timestamp": "2026-01-01T10:00:00Z",
        }]),
        source_system="simulator",
        check_database=False,
    )

    batch = DataQualityService(db_session).persist_assessment(assessment)

    assert batch.id is not None
    assert float(batch.quality_score) == 100.0
    assert batch.total_records == 1
