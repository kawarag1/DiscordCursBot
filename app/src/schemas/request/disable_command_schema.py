from pydantic import BaseModel


class DisableCommandSchema(BaseModel):
    guild_id: int
    command_name: str