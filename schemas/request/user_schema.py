from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    ds_id: int
    nickname: str
    avatar_url: str
    tag: str
    created_at: datetime