"""
File model for uploaded files in a workspace.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    table_name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', workspace_id={self.workspace_id}, storage_path='{self.storage_path}')>"
