from pydantic import BaseModel

class GuildSchema(BaseModel):
    id: str
    name: str
    icon_url: str | None
    approximate_member_count: int | None
    