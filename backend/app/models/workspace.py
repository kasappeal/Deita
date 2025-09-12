"""
Workspace models for database schema.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Workspace(Base):
    """Core workspace model for organizing user data and analysis."""

    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    is_public = Column(Boolean, default=True, nullable=False)
    is_orphan = Column(Boolean, default=False, nullable=False, index=True)
    storage_quota_bytes = Column(BigInteger, default=52428800, nullable=False)  # 50MB default for orphan
    settings = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    usage = relationship("WorkspaceUsage", back_populates="workspace", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("WorkspaceAuditLog", back_populates="workspace", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"


class WorkspaceUsage(Base):
    """Track workspace usage metrics for quota management and analytics."""

    __tablename__ = "workspace_usage"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), primary_key=True)
    file_count = Column(Integer, default=0, nullable=False)
    storage_used_bytes = Column(BigInteger, default=0, nullable=False)
    query_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="usage")
    
    def __repr__(self):
        return f"<WorkspaceUsage(workspace_id={self.workspace_id}, storage_used={self.storage_used_bytes})>"


class WorkspaceAuditLog(Base):
    """Audit log for workspace operations to ensure GDPR compliance."""

    __tablename__ = "workspace_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<WorkspaceAuditLog(id={self.id}, action='{self.action}', workspace_id={self.workspace_id})>"