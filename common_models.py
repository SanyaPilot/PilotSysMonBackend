from pydantic import BaseModel
from typing import Optional


class GenericResponseModel(BaseModel):
    status: str
    code: Optional[int]
    details: Optional[str]
