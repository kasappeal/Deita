"""
Health check and hello world schemas.
"""
from datetime import datetime

from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Health check response schema."""
    status: str
    message: str
    version: str
    timestamp: datetime

class HelloWorld(BaseModel):
    """Hello world response schema."""
    message: str
    version: str
    environment: str
