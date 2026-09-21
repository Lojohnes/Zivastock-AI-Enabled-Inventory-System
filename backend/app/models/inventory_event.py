from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class InventoryEvent(Base):
    """Canonical inventory movement captured from an operational source."""

    __tablename__ = "inventory_events"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(30), nullable=False, index=True)
    quantity = Column(Numeric(18, 4), nullable=False)
    unit_cost = Column(Numeric(18, 4), nullable=True)
    transaction_value = Column(Numeric(18, 4), nullable=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    source_system = Column(String(50), nullable=False, index=True)
    source_record_id = Column(String(150), nullable=False)
    reference_number = Column(String(150), nullable=True, index=True)
    stocktake_session_id = Column(
        BigInteger,
        ForeignKey("stocktake_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    import_batch_id = Column(
        BigInteger,
        ForeignKey("imports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_validated = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")
    user = relationship("User")
    stocktake_session = relationship("StocktakeSession")
    import_batch = relationship("ImportJob")

    __table_args__ = (
        UniqueConstraint(
            "source_system",
            "source_record_id",
            name="uq_inventory_event_source_record",
        ),
        CheckConstraint(
            "event_type IN ('SALE', 'PURCHASE', 'RECEIPT', 'RETURN', 'TRANSFER', 'STOCKTAKE', 'COUNT', 'ADJUSTMENT', 'WASTE', 'DAMAGE', 'PRICE_CHANGE', 'LOCATION_CHANGE', 'OPENING_BALANCE', 'CLOSING_BALANCE')",
            name="chk_inventory_event_type",
        ),
        CheckConstraint("quantity >= 0", name="chk_inventory_event_quantity_nonneg"),
        CheckConstraint("unit_cost IS NULL OR unit_cost >= 0", name="chk_inventory_event_unit_cost_nonneg"),
    )
