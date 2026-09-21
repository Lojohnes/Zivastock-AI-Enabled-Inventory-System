from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib
from app.core.database import Base


class StocktakeSession(Base):
    __tablename__ = "stocktake_sessions"

    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(Uuid(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location_id = Column(BigInteger, ForeignKey("locations.id"), nullable=False, index=True)
    session_type = Column(String(20), default="full", nullable=False)
    status = Column(String(20), default="not_started", nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    approved_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    location = relationship("Location", back_populates="sessions")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_sessions")
    first_counts = relationship("FirstCount", back_populates="session")
    second_counts = relationship("SecondCount", back_populates="session")
    adjustments = relationship("Adjustment", back_populates="session")
    assignments = relationship("SessionAssignment", back_populates="session")


class SessionAssignment(Base):
    __tablename__ = "session_assignments"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("stocktake_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    shelf_section_id = Column(BigInteger, ForeignKey("shelf_sections.id", ondelete="CASCADE"), nullable=True, index=True)
    assignment_role = Column(String(20), default="first_counter", nullable=False)
    status = Column(String(20), default="assigned", nullable=False)
    assigned_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session = relationship("StocktakeSession", back_populates="assignments")
    user = relationship("User", foreign_keys=[user_id])
    shelf_section = relationship("ShelfSection")
