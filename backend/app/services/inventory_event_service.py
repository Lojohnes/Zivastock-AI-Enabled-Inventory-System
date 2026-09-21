from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.inventory_event import InventoryEvent
from app.models.location import Location
from app.models.product import Product
from app.schemas.inventory_event import InventoryEventCreate


class InventoryEventService:
    """Validates and persists canonical inventory events idempotently."""

    DEFAULT_MAPPING = {
        "product_id": "product_id",
        "product_code": "product_code",
        "sku": "sku",
        "barcode": "barcode",
        "location_id": "location_id",
        "location_name": "location_name",
        "event_type": "event_type",
        "quantity": "quantity",
        "unit_cost": "unit_cost",
        "transaction_value": "transaction_value",
        "event_timestamp": "event_timestamp",
        "user_id": "user_id",
        "source_record_id": "source_record_id",
        "reference_number": "reference_number",
    }

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _value(row: dict[str, Any], mapping: dict[str, str], field: str, default=None):
        column = mapping.get(field, field)
        value = row.get(column, default)
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        if pd.isna(value):
            return default
        return value

    @staticmethod
    def _decimal(value: Any, field: str, allow_none: bool = True) -> Optional[Decimal]:
        if value is None or value == "":
            if allow_none:
                return None
            raise ValueError(f"{field} is required")
        try:
            result = Decimal(str(value).strip())
        except (InvalidOperation, AttributeError):
            raise ValueError(f"{field} must be numeric") from None
        if not result.is_finite():
            raise ValueError(f"{field} must be finite")
        return result

    def _resolve_product(self, data: InventoryEventCreate) -> Product:
        if data.product_id is not None:
            product = self.db.query(Product).filter(Product.id == data.product_id).first()
        else:
            product = None
            for field in ("barcode", "sku", "product_code"):
                value = getattr(data, field)
                if value:
                    product = self.db.query(Product).filter(getattr(Product, field) == value).first()
                    if product:
                        break
        if not product:
            raise ValueError("Product could not be resolved")
        return product

    def _resolve_location(self, data: InventoryEventCreate) -> Optional[int]:
        if data.location_id is not None:
            location = self.db.query(Location).filter(Location.id == data.location_id).first()
            if not location:
                raise ValueError("Location could not be resolved")
            return location.id
        if data.location_name:
            location = self.db.query(Location).filter(Location.name == data.location_name).first()
            if not location:
                raise ValueError("Location could not be resolved")
            return location.id
        return None

    def create_event(self, event_data: InventoryEventCreate) -> tuple[InventoryEvent, bool]:
        """Create an event, returning ``(event, is_duplicate)``."""
        existing = self.db.query(InventoryEvent).filter(
            InventoryEvent.source_system == event_data.source_system,
            InventoryEvent.source_record_id == event_data.source_record_id,
        ).first()
        if existing:
            return existing, True

        product = self._resolve_product(event_data)
        location_id = self._resolve_location(event_data)
        event = InventoryEvent(
            product_id=product.id,
            location_id=location_id,
            event_type=event_data.event_type,
            quantity=event_data.quantity,
            unit_cost=event_data.unit_cost,
            transaction_value=event_data.transaction_value,
            event_timestamp=event_data.event_timestamp,
            user_id=event_data.user_id,
            source_system=event_data.source_system,
            source_record_id=event_data.source_record_id,
            reference_number=event_data.reference_number,
            stocktake_session_id=event_data.stocktake_session_id,
            import_batch_id=event_data.import_batch_id,
        )
        self.db.add(event)
        self.db.flush()
        return event, False

    def ingest_dataframe(
        self,
        dataframe: pd.DataFrame,
        source_system: str,
        mapping: Optional[dict[str, str]] = None,
        import_batch_id: Optional[int] = None,
    ) -> dict:
        """Validate and ingest tabular transaction data in one transaction."""
        mapping = {**self.DEFAULT_MAPPING, **(mapping or {})}
        total = len(dataframe)
        accepted = 0
        duplicates = 0
        errors: list[str] = []
        event_ids: list[int] = []

        for row_index, row in dataframe.iterrows():
            row_number = row_index + 2
            try:
                raw = row.to_dict()
                timestamp_value = self._value(raw, mapping, "event_timestamp")
                timestamp = pd.to_datetime(timestamp_value, utc=True, errors="coerce")
                if pd.isna(timestamp):
                    raise ValueError("event_timestamp is invalid")

                source_record_id = self._value(raw, mapping, "source_record_id")
                if source_record_id is None:
                    raise ValueError("source_record_id is required")

                event_data = InventoryEventCreate(
                    product_id=self._optional_int(self._value(raw, mapping, "product_id")),
                    product_code=self._optional_text(self._value(raw, mapping, "product_code")),
                    sku=self._optional_text(self._value(raw, mapping, "sku")),
                    barcode=self._optional_text(self._value(raw, mapping, "barcode")),
                    location_id=self._optional_int(self._value(raw, mapping, "location_id")),
                    location_name=self._optional_text(self._value(raw, mapping, "location_name")),
                    event_type=str(self._value(raw, mapping, "event_type", "")).strip().upper(),
                    quantity=self._decimal(self._value(raw, mapping, "quantity"), "quantity", False),
                    unit_cost=self._decimal(self._value(raw, mapping, "unit_cost"), "unit_cost"),
                    transaction_value=self._decimal(self._value(raw, mapping, "transaction_value"), "transaction_value"),
                    event_timestamp=timestamp.to_pydatetime().astimezone(timezone.utc),
                    user_id=self._optional_int(self._value(raw, mapping, "user_id")),
                    source_system=source_system,
                    source_record_id=str(source_record_id).strip(),
                    reference_number=self._optional_text(self._value(raw, mapping, "reference_number")),
                    import_batch_id=import_batch_id,
                )
                event, is_duplicate = self.create_event(event_data)
                if is_duplicate:
                    duplicates += 1
                else:
                    accepted += 1
                event_ids.append(event.id)
            except Exception as exc:
                errors.append(f"Row {row_number}: {exc}")

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return {
            "total_records": total,
            "accepted_records": accepted,
            "duplicate_records": duplicates,
            "rejected_records": len(errors),
            "errors": errors[:100],
            "event_ids": event_ids,
        }

    @staticmethod
    def _optional_text(value: Any) -> Optional[str]:
        if value is None or str(value).strip() == "":
            return None
        return str(value).strip()

    @staticmethod
    def _optional_int(value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError("value must be an integer") from None
