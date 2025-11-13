from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str

class StatusResponse(BaseModel):
    status: str
    uptime: str
    version: str
