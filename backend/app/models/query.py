"""
Query model for saved SQL queries.
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Query(Base):
    __tablename__ = "queries"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False)
    sql_text = Column(Text, nullable=False)
    ai_generated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workspace = relationship("Workspace", backref="queries")

    def __repr__(self):
        return f"<Query(id={self.id}, name='{self.name}', workspace_id={self.workspace_id})>"
