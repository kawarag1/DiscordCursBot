from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

class UserCreate(BaseModel):
    ds_id: int
    nickname: str
    avatar_url: str
    created_at: datetime
    message_count: int
    level: int
    warnings: int = 0
    guild_id: int