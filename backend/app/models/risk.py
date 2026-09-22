from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class InventoryRiskScore(Base):
    __tablename__ = "inventory_risk_scores"

    id = Column(BigInteger, primary_key=True, index=True)
    analysis_key = Column(String(100), nullable=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    calculation_date = Column(Date, nullable=False, index=True)
    anomaly_score = Column(Numeric(8, 4), nullable=False, default=0)
    variance_score = Column(Numeric(8, 4), nullable=False, default=0)
    financial_value_score = Column(Numeric(8, 4), nullable=False, default=0)
    stockout_score = Column(Numeric(8, 4), nullable=False, default=0)
    adjustment_score = Column(Numeric(8, 4), nullable=False, default=0)
    accuracy_score = Column(Numeric(8, 4), nullable=False, default=0)
    criticality_score = Column(Numeric(8, 4), nullable=False, default=0)
    total_score = Column(Numeric(8, 4), nullable=False, default=0, index=True)
    risk_level = Column(String(20), nullable=False, default="LOW", index=True)
    abc_class = Column(String(1), nullable=True, index=True)
    priority = Column(String(30), nullable=False, default="MONITOR")
    explanation = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    calculation_version = Column(String(50), nullable=False, default="v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")

    __table_args__ = (
        CheckConstraint("total_score >= 0 AND total_score <= 100", name="chk_inventory_risk_score_range"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_inventory_risk_level"),
        CheckConstraint("abc_class IS NULL OR abc_class IN ('A', 'B', 'C')", name="chk_inventory_risk_abc_class"),
    )
