"""
Pydantic schemas for File model (upload, response).
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str
    size: int

class FileCreate(BaseModel):
    filename: str
    size: int

class File(FileBase):
    id: uuid.UUID
    table_name: str
    row_count: int
    csv_metadata: dict[str, Any] | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}
