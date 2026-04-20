from datetime import datetime

from pydantic import BaseModel

class BanSchema(BaseModel):
    user_id: int
    guild_id: int
    action: str
    target_id: int
    reason: str
    details: str
    created_at: datetime