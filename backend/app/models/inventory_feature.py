from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class InventoryFeatureSnapshot(Base):
    __tablename__ = "inventory_feature_snapshots"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="CASCADE"), nullable=True, index=True)
    feature_date = Column(Date, nullable=False, index=True)
    lookback_days = Column(Integer, nullable=False, default=30)
    feature_set_version = Column(String(50), nullable=False, default="v1")
    current_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    average_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    minimum_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    maximum_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    daily_sales = Column(Numeric(18, 4), nullable=False, default=0)
    weekly_sales = Column(Numeric(18, 4), nullable=False, default=0)
    sales_velocity = Column(Numeric(18, 4), nullable=False, default=0)
    demand_variability = Column(Numeric(18, 4), nullable=False, default=0)
    sales_value = Column(Numeric(18, 4), nullable=False, default=0)
    inventory_value = Column(Numeric(18, 4), nullable=False, default=0)
    variance_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    variance_percentage = Column(Numeric(18, 4), nullable=False, default=0)
    historical_variance = Column(Numeric(18, 4), nullable=False, default=0)
    adjustment_frequency = Column(Integer, nullable=False, default=0)
    count_disagreement = Column(Integer, nullable=False, default=0)
    days_of_inventory = Column(Numeric(18, 4), nullable=True)
    abc_class = Column(String(1), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "location_id",
            "feature_date",
            "feature_set_version",
            name="uq_inventory_feature_snapshot",
        ),
    )
