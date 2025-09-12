"""
Workspace model for organizing files, tables, and queries.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Workspace(Base):
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_PRIVATE = "private"

    __tablename__ = "workspaces"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name = Column(String, nullable=False)
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    visibility = Column(String, nullable=False, default=VISIBILITY_PUBLIC)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    max_file_size = Column(Integer, nullable=False)
    max_storage = Column(Integer, nullable=False)
    storage_used = Column(Integer, nullable=False, default=0)

    # Relationships
    owner = relationship("User", back_populates="workspaces")

    @property
    def is_orphaned(self) -> bool:
        return self.owner_id is None

    @property
    def is_public(self) -> bool:
        return self.visibility == self.VISIBILITY_PUBLIC # type: ignore

    @property
    def is_private(self) -> bool:
        return self.visibility == self.VISIBILITY_PRIVATE # type: ignore

    def __repr__(self):
        return f"<Workspace(id={self.id}, name='{self.name}', visibility='{self.visibility}')>"
