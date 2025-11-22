from pydantic import BaseModel

class OCRLocalRequest(BaseModel):
    img_path: str
    category: str = None
