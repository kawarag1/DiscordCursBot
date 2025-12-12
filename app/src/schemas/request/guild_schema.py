from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class GuildSchema(BaseModel):
    id: int
    name: str
    config_json: Optional[str]