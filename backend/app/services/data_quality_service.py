from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.data_quality import DataQualityBatch, DataQualityIssue
from app.models.inventory_event import InventoryEvent
from app.models.location import Location
from app.models.product import Product
from app.schemas.inventory_event import EVENT_TYPES


class DataQualityService:
    """Profile imported event data before it is used for analytics or ML."""

    REQUIRED_FIELDS = ("source_record_id", "event_type", "quantity", "event_timestamp")

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    @staticmethod
    def _value(row: dict[str, Any], mapping: dict[str, str], field: str, default=None):
        value = row.get(mapping.get(field, field), default)
        if value is None or pd.isna(value):
            return default
        return value

    @staticmethod
    def _json_value(value: Any):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        return str(value)

    def assess_dataframe(
        self,
        dataframe: pd.DataFrame,
        source_system: str,
        mapping: Optional[dict[str, str]] = None,
        check_database: bool = True,
    ) -> dict:
        mapping = mapping or {}
        issues: list[dict] = []
        duplicate_counts = Counter()
        seen_source_ids: set[str] = set()
        existing_source_ids: set[str] = set()

        if self.db and check_database and not dataframe.empty:
            source_column = mapping.get("source_record_id", "source_record_id")
            source_ids = {
                str(value).strip()
                for value in dataframe[source_column].dropna().tolist()
                if str(value).strip()
            } if source_column in dataframe.columns else set()
            if source_ids:
                existing_source_ids = {
                    value for (value,) in self.db.query(InventoryEvent.source_record_id).filter(
                        InventoryEvent.source_system == source_system,
                        InventoryEvent.source_record_id.in_(source_ids),
                    ).all()
                }

        for row_index, row in dataframe.iterrows():
            row_number = int(row_index) + 2
            raw = row.to_dict()
            source_record_id = self._value(raw, mapping, "source_record_id")
            source_record_id = str(source_record_id).strip() if source_record_id is not None else None
            if source_record_id:
                duplicate_counts[source_record_id] += 1

            def add_issue(issue_type: str, description: str, field_name: Optional[str] = None, severity: str = "error", value: Any = None):
                issues.append({
                    "record_reference": source_record_id,
                    "row_number": row_number,
                    "issue_type": issue_type,
                    "field_name": field_name,
                    "severity": severity,
                    "description": description,
                    "raw_value": self._json_value(value),
                })

            for field in self.REQUIRED_FIELDS:
                value = self._value(raw, mapping, field)
                if value is None or (isinstance(value, str) and not value.strip()):
                    add_issue("missing_value", f"Required field '{field}' is missing", field)

            event_type = str(self._value(raw, mapping, "event_type", "")).strip().upper()
            if event_type and event_type not in EVENT_TYPES:
                add_issue("invalid_event_type", f"Unsupported event type: {event_type}", "event_type", value=event_type)

            quantity = self._value(raw, mapping, "quantity")
            try:
                quantity_value = float(quantity)
                if quantity_value < 0:
                    add_issue("invalid_quantity", "Quantity cannot be negative", "quantity", value=quantity)
            except (TypeError, ValueError):
                if quantity is not None:
                    add_issue("invalid_quantity", "Quantity must be numeric", "quantity", value=quantity)

            timestamp_value = self._value(raw, mapping, "event_timestamp")
            timestamp = pd.to_datetime(timestamp_value, utc=True, errors="coerce")
            if timestamp_value is not None and pd.isna(timestamp):
                add_issue("invalid_timestamp", "Event timestamp is invalid", "event_timestamp", value=timestamp_value)
            elif not pd.isna(timestamp) and timestamp.to_pydatetime() > datetime.now(timezone.utc):
                add_issue(
                    "future_timestamp",
                    "Event timestamp is in the future",
                    "event_timestamp",
                    severity="warning",
                    value=timestamp_value,
                )

            if source_record_id:
                if source_record_id in existing_source_ids:
                    add_issue("duplicate_source_record", "Source record already exists", "source_record_id", "warning", source_record_id)
                elif source_record_id in seen_source_ids:
                    add_issue("duplicate_source_record", "Source record is repeated in this dataset", "source_record_id", "warning", source_record_id)
                seen_source_ids.add(source_record_id)

            if self.db:
                product_match = any(self._value(raw, mapping, field) for field in ("product_id", "barcode", "sku", "product_code"))
                if not product_match:
                    add_issue("missing_product_identifier", "No product identifier was supplied", "product_id")
                else:
                    product = self._resolve_product(raw, mapping)
                    if not product:
                        add_issue("invalid_product", "Product could not be resolved", "product_id")

                location_identifier = self._value(raw, mapping, "location_id") or self._value(raw, mapping, "location_name")
                if location_identifier and not self._resolve_location(raw, mapping):
                    add_issue("invalid_location", "Location could not be resolved", "location_id", value=location_identifier)

        total = len(dataframe)
        invalid_row_numbers = {issue["row_number"] for issue in issues if issue["severity"] == "error"}
        duplicate_rows = {issue["row_number"] for issue in issues if issue["issue_type"] == "duplicate_source_record"}
        valid_records = max(0, total - len(invalid_row_numbers) - len(duplicate_rows - invalid_row_numbers))
        missing_value_count = sum(issue["issue_type"] == "missing_value" for issue in issues)
        duplicate_records = len(duplicate_rows)
        quality_score = round((valid_records / total) * 100, 2) if total else 0.0

        issue_summary = dict(Counter(issue["issue_type"] for issue in issues))
        return {
            "dataset_type": "inventory_events",
            "source_system": source_system,
            "quality_score": quality_score,
            "total_records": total,
            "valid_records": valid_records,
            "invalid_records": len(invalid_row_numbers),
            "duplicate_records": duplicate_records,
            "missing_value_count": missing_value_count,
            "issue_summary": issue_summary,
            "issues": issues,
        }

    def persist_assessment(
        self,
        assessment: dict,
        import_batch_id: Optional[int] = None,
    ) -> DataQualityBatch:
        if not self.db:
            raise ValueError("A database session is required to persist data-quality results")

        batch = DataQualityBatch(
            import_batch_id=import_batch_id,
            dataset_type=assessment["dataset_type"],
            source_system=assessment["source_system"],
            quality_score=assessment["quality_score"],
            total_records=assessment["total_records"],
            valid_records=assessment["valid_records"],
            invalid_records=assessment["invalid_records"],
            duplicate_records=assessment["duplicate_records"],
            missing_value_count=assessment["missing_value_count"],
            issue_summary=assessment["issue_summary"],
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(batch)
        self.db.flush()
        for issue in assessment["issues"]:
            self.db.add(DataQualityIssue(batch_id=batch.id, **issue))
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def _resolve_product(self, row: dict[str, Any], mapping: dict[str, str]) -> Optional[Product]:
        if not self.db:
            return None
        product_id = self._value(row, mapping, "product_id")
        if product_id:
            return self.db.query(Product).filter(Product.id == product_id).first()
        for field in ("barcode", "sku", "product_code"):
            value = self._value(row, mapping, field)
            if value:
                product = self.db.query(Product).filter(getattr(Product, field) == value).first()
                if product:
                    return product
        return None

    def _resolve_location(self, row: dict[str, Any], mapping: dict[str, str]) -> Optional[Location]:
        if not self.db:
            return None
        location_id = self._value(row, mapping, "location_id")
        if location_id:
            return self.db.query(Location).filter(Location.id == location_id).first()
        location_name = self._value(row, mapping, "location_name")
        if location_name:
            return self.db.query(Location).filter(Location.name == location_name).first()
        return None
