"""
Pydantic schemas for File model (upload, response).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str
    size: int

class FileCreate(BaseModel):
    filename: str
    size: int

class File(FileBase):
    id: uuid.UUID
    uploaded_at: datetime

    model_config = {"from_attributes": True}
