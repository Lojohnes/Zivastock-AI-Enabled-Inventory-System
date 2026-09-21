from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib
from app.core.database import Base


class ImportJob(Base):
    __tablename__ = "imports"

    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(Uuid(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    entity_type = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False, default="")
    file_path = Column(String(512), nullable=True)
    status = Column(String(30), default="pending", nullable=False, index=True)
    total_records = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    mapping_config = Column(JSONB().with_variant(JSON, "sqlite"), nullable=True)
    error_log = Column(JSONB().with_variant(JSON, "sqlite"), nullable=True)
    uploaded_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    uploader = relationship("User")
