import pandas as pd

from app.models.product import Product
from app.services.inventory_event_service import InventoryEventService


def test_ingest_events_resolves_products_and_deduplicates(db_session):
    product = Product(
        barcode="SIM-001",
        product_code="P001",
        description="Test Product",
        unit_of_measure="EA",
        system_quantity=100,
        unit_cost=10,
    )
    db_session.add(product)
    db_session.commit()

    dataframe = pd.DataFrame([
        {
            "source_record_id": "SALE-001",
            "barcode": "SIM-001",
            "event_type": "sale",
            "quantity": 3,
            "event_timestamp": "2026-01-01T10:00:00Z",
            "unit_cost": 10,
        },
        {
            "source_record_id": "SALE-001",
            "barcode": "SIM-001",
            "event_type": "SALE",
            "quantity": 3,
            "event_timestamp": "2026-01-01T10:00:00Z",
            "unit_cost": 10,
        },
        {
            "source_record_id": "SALE-002",
            "barcode": "UNKNOWN",
            "event_type": "SALE",
            "quantity": 1,
            "event_timestamp": "2026-01-01T11:00:00Z",
            "unit_cost": 10,
        },
    ])

    result = InventoryEventService(db_session).ingest_dataframe(dataframe, "simulator")

    assert result["total_records"] == 3
    assert result["accepted_records"] == 1
    assert result["duplicate_records"] == 1
    assert result["rejected_records"] == 1
    assert len(result["event_ids"]) == 2
    assert "Product could not be resolved" in result["errors"][0]
