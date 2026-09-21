from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DataQualityBatch(Base):
    __tablename__ = "data_quality_batches"

    id = Column(BigInteger, primary_key=True, index=True)
    import_batch_id = Column(BigInteger, ForeignKey("imports.id", ondelete="SET NULL"), nullable=True, index=True)
    dataset_type = Column(String(50), nullable=False)
    source_system = Column(String(50), nullable=False)
    quality_score = Column(Numeric(6, 2), nullable=False)
    total_records = Column(Integer, nullable=False, default=0)
    valid_records = Column(Integer, nullable=False, default=0)
    invalid_records = Column(Integer, nullable=False, default=0)
    duplicate_records = Column(Integer, nullable=False, default=0)
    missing_value_count = Column(Integer, nullable=False, default=0)
    issue_summary = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    import_batch = relationship("ImportJob")
    issues = relationship("DataQualityIssue", back_populates="batch", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("quality_score >= 0 AND quality_score <= 100", name="chk_quality_score_range"),
        CheckConstraint("total_records >= 0", name="chk_quality_total_nonneg"),
        CheckConstraint("valid_records >= 0 AND invalid_records >= 0", name="chk_quality_valid_invalid_nonneg"),
    )


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id = Column(BigInteger, primary_key=True, index=True)
    batch_id = Column(BigInteger, ForeignKey("data_quality_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    record_reference = Column(String(150), nullable=True, index=True)
    row_number = Column(Integer, nullable=True)
    issue_type = Column(String(50), nullable=False, index=True)
    field_name = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=False, default="error")
    description = Column(Text, nullable=False)
    raw_value = Column(JSONB().with_variant(JSON, "sqlite"), nullable=True)
    resolved = Column(String(20), nullable=False, default="open")
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    batch = relationship("DataQualityBatch", back_populates="issues")

    __table_args__ = (
        CheckConstraint("severity IN ('info', 'warning', 'error')", name="chk_quality_issue_severity"),
        CheckConstraint("resolved IN ('open', 'resolved', 'ignored')", name="chk_quality_issue_status"),
    )
