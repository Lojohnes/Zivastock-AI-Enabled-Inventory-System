from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(BigInteger, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    algorithm = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    dataset_version = Column(String(100), nullable=True)
    feature_set_version = Column(String(100), nullable=True)
    features = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    hyperparameters = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    training_start = Column(Date, nullable=True)
    training_end = Column(Date, nullable=True)
    evaluation_metrics = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    artifact_path = Column(String(512), nullable=True)
    status = Column(String(30), nullable=False, default="evaluated", index=True)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    creator = relationship("User")
    anomaly_results = relationship("AnomalyResult", back_populates="model_version")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'trained', 'evaluated', 'selected', 'retired')", name="chk_model_version_status"),
    )


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(BigInteger, primary_key=True, index=True)
    analysis_key = Column(String(100), nullable=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    feature_date = Column(Date, nullable=False, index=True)
    model_version_id = Column(BigInteger, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    algorithm = Column(String(100), nullable=False)
    anomaly_flag = Column(Integer, nullable=False, default=0)
    anomaly_score = Column(Numeric(8, 4), nullable=False, default=0)
    risk_level = Column(String(20), nullable=False, default="LOW")
    threshold_used = Column(Numeric(8, 4), nullable=True)
    evidence = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    feature_contributions = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")
    model_version = relationship("ModelVersion", back_populates="anomaly_results")

    __table_args__ = (
        CheckConstraint("anomaly_flag IN (0, 1)", name="chk_anomaly_flag"),
        CheckConstraint("anomaly_score >= 0 AND anomaly_score <= 100", name="chk_anomaly_score_range"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_anomaly_risk_level"),
    )
