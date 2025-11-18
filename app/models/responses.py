from pydantic import BaseModel
from typing import Dict, Any, List

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str

class StatusResponse(BaseModel):
    status: str
    uptime: str
    version: str

class AppStatusResponse(BaseModel):
    service: str
    version: str
    uptime: str
    timestamp: str
    ocr_engine: Dict[str, Any]
    queue: Dict[str, Any]
    workers: Dict[str, Any]
    processing: Dict[str, Any]
    system: Dict[str, Any]
