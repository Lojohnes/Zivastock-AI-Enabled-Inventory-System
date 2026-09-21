from sqlalchemy import Column, BigInteger, SmallInteger, String, Boolean, DateTime, ForeignKey, Text, Uuid
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(Uuid(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=True)
    profile_picture = Column(Text, nullable=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(SmallInteger, default=0, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(INET().with_variant(String(45), "sqlite"), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    role = relationship("Role", back_populates="users")
    first_counts = relationship("FirstCount", back_populates="user", foreign_keys="FirstCount.user_id")
    second_counts = relationship("SecondCount", back_populates="user", foreign_keys="SecondCount.user_id")
    created_sessions = relationship("StocktakeSession", foreign_keys="StocktakeSession.created_by", back_populates="creator")
    audit_entries = relationship("AuditTrail", back_populates="user")
