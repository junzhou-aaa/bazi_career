from pydantic import BaseModel
from typing import Optional

class Company(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    industry_family: str
    size: Optional[str] = None
    url: Optional[str] = None
    source: str
    source_url: str
    source_last_verified_at: str
    created_at: str
    updated_at: str
