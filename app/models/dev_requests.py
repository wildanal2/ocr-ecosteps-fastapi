from pydantic import BaseModel

class OCRDevRequest(BaseModel):
    img_url: str
