from pydantic import BaseModel
from datetime import datetime


class RawActionSchema(BaseModel):
    id: int
    user_id: int
    guild_id: int
    action: str
    target_id: int
    reason: str
    details: str
    created_at: datetime