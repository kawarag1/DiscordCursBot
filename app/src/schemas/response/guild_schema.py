from pydantic import BaseModel

class GuildSchema(BaseModel):
    id: int
    name: str
    icon_url: str | None
    