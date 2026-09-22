from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(BigInteger, primary_key=True, index=True)
    analysis_key = Column(String(100), unique=True, nullable=False, index=True)
    analysis_type = Column(String(30), nullable=False, index=True)
    reference_id = Column(String(100), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="COMPLETED")
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    creator = relationship("User")

    __table_args__ = (
        CheckConstraint("status IN ('RUNNING', 'COMPLETED', 'FAILED')", name="chk_analysis_run_status"),
    )
