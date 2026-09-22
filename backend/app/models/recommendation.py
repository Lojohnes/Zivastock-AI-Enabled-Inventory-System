from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(BigInteger, primary_key=True, index=True)
    analysis_key = Column(String(100), nullable=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    recommendation_type = Column(String(40), nullable=False, index=True)
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String(30), nullable=False, default="MONITOR", index=True)
    confidence_score = Column(Numeric(6, 2), nullable=True)
    evidence = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    expected_impact = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    model_version_id = Column(BigInteger, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    product = relationship("Product")
    location = relationship("Location")
    model_version = relationship("ModelVersion")
    decisions = relationship("RecommendationDecision", back_populates="recommendation", cascade="all, delete-orphan")
    outcomes = relationship("RecommendationOutcome", back_populates="recommendation", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED', 'OVERRIDDEN', 'COMPLETED', 'EXPIRED')", name="chk_recommendation_status"),
        CheckConstraint("confidence_score IS NULL OR confidence_score BETWEEN 0 AND 100", name="chk_recommendation_confidence"),
    )


class RecommendationDecision(Base):
    __tablename__ = "recommendation_decisions"

    id = Column(BigInteger, primary_key=True, index=True)
    recommendation_id = Column(BigInteger, ForeignKey("ai_recommendations.id", ondelete="CASCADE"), nullable=False, index=True)
    decision = Column(String(20), nullable=False)
    decided_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision_reason = Column(Text, nullable=True)
    override_flag = Column(Integer, nullable=False, default=0)
    decided_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    recommendation = relationship("AIRecommendation", back_populates="decisions")
    user = relationship("User")

    __table_args__ = (
        CheckConstraint("decision IN ('APPROVED', 'REJECTED', 'OVERRIDDEN')", name="chk_recommendation_decision"),
        CheckConstraint("override_flag IN (0, 1)", name="chk_recommendation_override"),
    )


class RecommendationOutcome(Base):
    __tablename__ = "recommendation_outcomes"

    id = Column(BigInteger, primary_key=True, index=True)
    recommendation_id = Column(BigInteger, ForeignKey("ai_recommendations.id", ondelete="CASCADE"), nullable=False, index=True)
    actual_action = Column(String(100), nullable=True)
    outcome_status = Column(String(30), nullable=False)
    actual_result = Column(Text, nullable=True)
    variance_after_action = Column(Numeric(18, 4), nullable=True)
    stockout_avoided = Column(Integer, nullable=True)
    recorded_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    recommendation = relationship("AIRecommendation", back_populates="outcomes")
    user = relationship("User")

    __table_args__ = (
        CheckConstraint("outcome_status IN ('PENDING', 'SUCCESS', 'PARTIAL', 'FAILED', 'NOT_APPLICABLE')", name="chk_recommendation_outcome"),
        CheckConstraint("stockout_avoided IS NULL OR stockout_avoided IN (0, 1)", name="chk_stockout_avoided"),
    )
