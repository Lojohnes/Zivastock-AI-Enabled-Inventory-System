from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class SimulatedProduct:
    barcode: str
    product_code: str
    description: str
    unit_cost: float
    baseline_daily_demand: int


DEFAULT_PRODUCTS = (
    SimulatedProduct("SIM-COOK-2L", "SIM001", "Cooking Oil 2L", 8.50, 18),
    SimulatedProduct("SIM-RICE-5K", "SIM002", "Rice 5kg", 7.25, 12),
    SimulatedProduct("SIM-MILK-1L", "SIM003", "Fresh Milk 1L", 1.40, 25),
    SimulatedProduct("SIM-BEEF-1K", "SIM004", "Beef Sausages 1kg", 6.80, 10),
    SimulatedProduct("SIM-SUGAR-2K", "SIM005", "Sugar 2kg", 3.10, 8),
)


class TransactionSimulator:
    """Generate deterministic POS/ERP-like data for repeatable experiments."""

    SUPPORTED_SCENARIOS = {
        "normal",
        "high_demand",
        "abnormal_adjustment",
        "stock_discrepancy",
        "supplier_delay",
    }

    def __init__(self, seed: int = 42, products: Iterable[SimulatedProduct] = DEFAULT_PRODUCTS):
        self.seed = seed
        self.products = tuple(products)

    def generate(
        self,
        days: int = 30,
        scenario: str = "normal",
        start_date: datetime | None = None,
    ) -> pd.DataFrame:
        if days < 1:
            raise ValueError("days must be greater than zero")
        if scenario not in self.SUPPORTED_SCENARIOS:
            raise ValueError(f"Unsupported simulation scenario: {scenario}")

        self.random = random.Random(self.seed)
        start = start_date or datetime(2026, 1, 1, tzinfo=timezone.utc)
        rows: list[dict] = []
        sequence = 1

        for day_offset in range(days):
            event_date = start + timedelta(days=day_offset)
            for product in self.products:
                demand_multiplier = 1.0
                if scenario == "high_demand" and product.barcode in {"SIM-COOK-2L", "SIM-MILK-1L"}:
                    demand_multiplier = 1.8

                quantity = max(
                    0,
                    round(self.random.gauss(product.baseline_daily_demand * demand_multiplier, 2)),
                )
                rows.append(self._row(
                    sequence,
                    product,
                    "SALE",
                    quantity,
                    event_date + timedelta(hours=12),
                ))
                sequence += 1

                if day_offset % 7 == 0 and scenario != "supplier_delay":
                    receipt_quantity = product.baseline_daily_demand * 7
                    rows.append(self._row(
                        sequence,
                        product,
                        "RECEIPT",
                        receipt_quantity,
                        event_date + timedelta(hours=7),
                    ))
                    sequence += 1

                if day_offset % 10 == 0:
                    return_quantity = 1 if product.barcode == "SIM-MILK-1L" else 0
                    if return_quantity:
                        rows.append(self._row(
                            sequence,
                            product,
                            "RETURN",
                            return_quantity,
                            event_date + timedelta(hours=16),
                        ))
                        sequence += 1

        if scenario == "abnormal_adjustment":
            product = self.products[0]
            rows.append(self._row(
                sequence,
                product,
                "ADJUSTMENT",
                75,
                start + timedelta(days=max(days - 2, 0), hours=18),
                reference_number="SIM-ABNORMAL-ADJUSTMENT",
            ))
        elif scenario == "stock_discrepancy":
            product = self.products[0]
            rows.append(self._row(
                sequence,
                product,
                "ADJUSTMENT",
                23,
                start + timedelta(days=max(days - 1, 0), hours=20),
                reference_number="SIM-STOCK-DISCREPANCY",
            ))

        return pd.DataFrame(rows)

    @staticmethod
    def _row(
        sequence: int,
        product: SimulatedProduct,
        event_type: str,
        quantity: int,
        timestamp: datetime,
        reference_number: str | None = None,
    ) -> dict:
        return {
            "source_record_id": f"SIM-{sequence:06d}",
            "barcode": product.barcode,
            "product_code": product.product_code,
            "description": product.description,
            "location_name": "Main Store",
            "event_type": event_type,
            "quantity": quantity,
            "unit_cost": product.unit_cost,
            "transaction_value": round(quantity * product.unit_cost, 2),
            "event_timestamp": timestamp.isoformat(),
            "reference_number": reference_number or f"SIM-{event_type}-{sequence:06d}",
        }
