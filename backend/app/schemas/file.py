"""
Pydantic schemas for File model (upload, response).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str
    size: int
    file_type: str

class FileCreate(BaseModel):
    filename: str
    size: int
    file_type: str

class File(FileBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}
