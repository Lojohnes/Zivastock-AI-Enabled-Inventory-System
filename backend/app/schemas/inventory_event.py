from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


EVENT_TYPES = {
    "SALE",
    "PURCHASE",
    "RECEIPT",
    "RETURN",
    "TRANSFER",
    "STOCKTAKE",
    "COUNT",
    "ADJUSTMENT",
    "WASTE",
    "DAMAGE",
    "PRICE_CHANGE",
    "LOCATION_CHANGE",
    "OPENING_BALANCE",
    "CLOSING_BALANCE",
}


class InventoryEventCreate(BaseModel):
    product_id: Optional[int] = None
    product_code: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    event_type: str
    quantity: Decimal = Field(..., ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    transaction_value: Optional[Decimal] = None
    event_timestamp: datetime
    user_id: Optional[int] = None
    source_system: str = Field(..., min_length=1, max_length=50)
    source_record_id: str = Field(..., min_length=1, max_length=150)
    reference_number: Optional[str] = None
    stocktake_session_id: Optional[int] = None
    import_batch_id: Optional[int] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in EVENT_TYPES:
            raise ValueError(f"Unsupported inventory event type: {value}")
        return value


class InventoryEventResponse(BaseModel):
    id: int
    product_id: int
    location_id: Optional[int]
    event_type: str
    quantity: Decimal
    unit_cost: Optional[Decimal]
    transaction_value: Optional[Decimal]
    event_timestamp: datetime
    user_id: Optional[int]
    source_system: str
    source_record_id: str
    reference_number: Optional[str]
    stocktake_session_id: Optional[int]
    import_batch_id: Optional[int]
    is_validated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionIngestionResponse(BaseModel):
    total_records: int
    accepted_records: int
    duplicate_records: int
    rejected_records: int
    errors: list[str]
    event_ids: list[int]
