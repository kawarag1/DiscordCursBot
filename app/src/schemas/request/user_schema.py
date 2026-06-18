from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    ds_id: int
    nickname: str
    avatar_url: str
    created_at: datetime
    warnings: int = 0
    guild_id: int