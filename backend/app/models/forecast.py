from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    model_version_id = Column(BigInteger, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    model_algorithm = Column(String(50), nullable=False)
    forecast_date = Column(Date, nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False, default=7)
    predicted_demand = Column(Numeric(18, 4), nullable=False)
    lower_bound = Column(Numeric(18, 4), nullable=True)
    upper_bound = Column(Numeric(18, 4), nullable=True)
    actual_demand = Column(Numeric(18, 4), nullable=True)
    evaluation_metrics = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")


class InventoryExposure(Base):
    __tablename__ = "inventory_exposures"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    calculation_date = Column(Date, nullable=False, index=True)
    forecast_model = Column(String(50), nullable=False)
    current_quantity = Column(Numeric(18, 4), nullable=False)
    predicted_daily_demand = Column(Numeric(18, 4), nullable=False)
    safety_stock = Column(Numeric(18, 4), nullable=False, default=0)
    days_until_stockout = Column(Numeric(18, 4), nullable=True)
    stockout_date = Column(Date, nullable=True)
    stockout_risk = Column(String(20), nullable=False, default="LOW")
    excess_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    slow_moving = Column(Integer, nullable=False, default=0)
    non_moving = Column(Integer, nullable=False, default=0)
    explanation = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    calculation_version = Column(String(50), nullable=False, default="v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")

    __table_args__ = (
        CheckConstraint("stockout_risk IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_exposure_stockout_risk"),
        CheckConstraint("slow_moving IN (0, 1)", name="chk_exposure_slow_moving"),
        CheckConstraint("non_moving IN (0, 1)", name="chk_exposure_non_moving"),
    )
