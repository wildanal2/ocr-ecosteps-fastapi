from pydantic import BaseModel
from typing import Union

class OCRRequest(BaseModel):
    report_id: Union[int, str]
    user_id: Union[int, str]
    s3_url: str
