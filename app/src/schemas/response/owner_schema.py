from typing import Optional
from pydantic import BaseModel


class OwnerSchema(BaseModel):
    id: int
    ds_id: int
    email: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    session_token: Optional[str]
    expires_at: Optional[int]