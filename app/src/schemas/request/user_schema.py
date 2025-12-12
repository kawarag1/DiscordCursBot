from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    ds_id: int
    nickname: str
    avatar_url: str
    created_at: datetime
    message_count: int
    level: int
    guild_id: int