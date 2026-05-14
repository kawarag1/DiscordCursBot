from pydantic import BaseModel
from datetime import datetime


class MemberActionSchema(BaseModel):
    username: str
    avatar_url: str | None

class ActionSchema(BaseModel):
    id: int
    user_id: MemberActionSchema
    guild_id: int
    action: str
    target_id: MemberActionSchema
    reason: str
    details: str
    created_at: datetime



