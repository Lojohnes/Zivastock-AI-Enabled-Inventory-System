from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.inventory_event import InventoryEvent
from app.models.inventory_feature import InventoryFeatureSnapshot


OUTFLOW_EVENTS = {"SALE", "WASTE", "DAMAGE"}
INFLOW_EVENTS = {"PURCHASE", "RECEIPT", "RETURN", "OPENING_BALANCE"}


class FeatureEngineeringService:
    """Create leakage-safe, versioned inventory features from canonical events."""

    def __init__(self, db: Optional[Session] = None, feature_set_version: str = "v1"):
        self.db = db
        self.feature_set_version = feature_set_version

    def build_snapshots(
        self,
        events: pd.DataFrame,
        as_of_date: date,
        lookback_days: int = 30,
    ) -> pd.DataFrame:
        if lookback_days < 1:
            raise ValueError("lookback_days must be greater than zero")
        required = {"product_id", "event_type", "quantity", "event_timestamp"}
        missing = required - set(events.columns)
        if missing:
            raise ValueError(f"Missing event columns: {', '.join(sorted(missing))}")

        if events.empty:
            return self._empty_frame()

        frame = events.copy()
        frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce")
        frame = frame[frame["event_timestamp"].notna()]
        cutoff = pd.Timestamp(datetime.combine(as_of_date, time.max), tz="UTC")
        window_start = pd.Timestamp(datetime.combine(as_of_date, time.min), tz="UTC") - pd.Timedelta(days=lookback_days - 1)
        frame = frame[frame["event_timestamp"] <= cutoff]
        if frame.empty:
            return self._empty_frame()

        frame["location_id"] = frame.get("location_id", pd.Series(index=frame.index, dtype="Int64"))
        frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce").fillna(0).clip(lower=0)
        if "unit_cost" not in frame:
            frame["unit_cost"] = 0
        frame["unit_cost"] = pd.to_numeric(frame["unit_cost"], errors="coerce").fillna(0)
        frame["event_type"] = frame["event_type"].astype(str).str.upper()
        frame["signed_quantity"] = frame.apply(self._signed_quantity, axis=1)
        frame["event_date"] = frame["event_timestamp"].dt.date

        snapshots = []
        group_columns = ["product_id", "location_id"]
        for (product_id, location_id), group in frame.groupby(group_columns, dropna=False):
            group = group.sort_values("event_timestamp")
            window = group[group["event_timestamp"] >= window_start]
            if window.empty:
                window = group.iloc[0:0]

            daily = (
                window.groupby("event_date")["signed_quantity"]
                .sum()
                .reindex(pd.date_range(window_start.date(), as_of_date, freq="D").date, fill_value=0)
            )
            inventory_path = group["signed_quantity"].cumsum()
            current_quantity = float(inventory_path.iloc[-1]) if not inventory_path.empty else 0.0
            sales = window[window["event_type"] == "SALE"]
            sales_quantity = float(sales["quantity"].sum()) if not sales.empty else 0.0
            sales_value = float((sales["quantity"] * sales["unit_cost"]).sum()) if not sales.empty else 0.0
            adjustment = window[window["event_type"] == "ADJUSTMENT"]
            variance_quantity = float(adjustment["quantity"].sum()) if not adjustment.empty else 0.0
            average_daily_sales = sales_quantity / lookback_days
            last_unit_cost = float(group["unit_cost"].iloc[-1]) if not group.empty else 0.0

            snapshots.append({
                "product_id": int(product_id),
                "location_id": self._optional_int(location_id),
                "feature_date": as_of_date,
                "lookback_days": lookback_days,
                "feature_set_version": self.feature_set_version,
                "current_quantity": current_quantity,
                "average_quantity": float(inventory_path.mean()) if not inventory_path.empty else 0.0,
                "minimum_quantity": float(inventory_path.min()) if not inventory_path.empty else 0.0,
                "maximum_quantity": float(inventory_path.max()) if not inventory_path.empty else 0.0,
                "daily_sales": average_daily_sales,
                "weekly_sales": average_daily_sales * 7,
                "sales_velocity": average_daily_sales,
                "demand_variability": float(daily.std(ddof=0)),
                "sales_value": sales_value,
                "inventory_value": current_quantity * last_unit_cost,
                "variance_quantity": variance_quantity,
                "variance_percentage": (variance_quantity / abs(current_quantity) * 100) if current_quantity else 0.0,
                "historical_variance": variance_quantity,
                "adjustment_frequency": int(len(adjustment)),
                "count_disagreement": int(window["event_type"].eq("COUNT").sum() > 1),
                "days_of_inventory": (current_quantity / average_daily_sales) if average_daily_sales > 0 else None,
                "abc_class": None,
            })

        result = pd.DataFrame(snapshots)
        if result.empty:
            return self._empty_frame()
        result["abc_class"] = self._assign_abc_classes(result["sales_value"])
        return result

    def generate_from_database(self, as_of_date: date, lookback_days: int = 30) -> pd.DataFrame:
        if not self.db:
            raise ValueError("A database session is required")
        cutoff = datetime.combine(as_of_date, time.max).replace(tzinfo=timezone.utc)
        events = self.db.query(InventoryEvent).filter(InventoryEvent.event_timestamp <= cutoff).all()
        rows = [
            {
                "product_id": event.product_id,
                "location_id": event.location_id,
                "event_type": event.event_type,
                "quantity": float(event.quantity),
                "unit_cost": float(event.unit_cost or 0),
                "event_timestamp": event.event_timestamp,
            }
            for event in events
        ]
        return self.build_snapshots(pd.DataFrame(rows), as_of_date, lookback_days)

    def persist_snapshots(self, snapshots: pd.DataFrame) -> int:
        if not self.db:
            raise ValueError("A database session is required")
        count = 0
        for row in snapshots.to_dict("records"):
            filters = {
                "product_id": row["product_id"],
                "location_id": row["location_id"],
                "feature_date": row["feature_date"],
                "feature_set_version": row["feature_set_version"],
            }
            snapshot = self.db.query(InventoryFeatureSnapshot).filter_by(**filters).first()
            if snapshot is None:
                snapshot = InventoryFeatureSnapshot(**filters)
                self.db.add(snapshot)
            for field, value in row.items():
                if field not in filters:
                    setattr(snapshot, field, value)
            count += 1
        self.db.commit()
        return count

    @staticmethod
    def _signed_quantity(row) -> float:
        quantity = float(row["quantity"])
        if row["event_type"] in OUTFLOW_EVENTS:
            return -quantity
        if row["event_type"] in INFLOW_EVENTS:
            return quantity
        return 0.0

    @staticmethod
    def _optional_int(value):
        return None if pd.isna(value) else int(value)

    @staticmethod
    def _assign_abc_classes(sales_values: pd.Series) -> list[str]:
        if sales_values.empty:
            return []
        ordered = sales_values.sort_values(ascending=False)
        total = float(ordered.sum())
        if total <= 0:
            return ["C"] * len(sales_values)
        cumulative = ordered.cumsum() / total * 100
        classes = {}
        for index, percentage in cumulative.items():
            prior_percentage = percentage - (float(ordered.loc[index]) / total * 100)
            classes[index] = "A" if prior_percentage < 80 else "B" if prior_percentage < 95 else "C"
        return [classes[index] for index in sales_values.index]

    @staticmethod
    def _empty_frame() -> pd.DataFrame:
        return pd.DataFrame(columns=[
            "product_id", "location_id", "feature_date", "lookback_days", "feature_set_version",
            "current_quantity", "average_quantity", "minimum_quantity", "maximum_quantity",
            "daily_sales", "weekly_sales", "sales_velocity", "demand_variability", "sales_value",
            "inventory_value", "variance_quantity", "variance_percentage", "historical_variance",
            "adjustment_frequency", "count_disagreement", "days_of_inventory", "abc_class",
        ])
