from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    ds_id: int
    nickname: str
    avatar_url: str
    created_at: datetime
    message_count: int
    level: int
    guild_id: int

    model_config = ConfigDict(from_attributes = True)