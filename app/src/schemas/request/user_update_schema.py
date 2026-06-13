from typing import Optional
from pydantic import BaseModel

class UserUpdate(BaseModel):
    ds_id: int
    nickname: str
    avatar_url: Optional[str]
    warnings: int