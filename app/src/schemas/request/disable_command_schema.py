from pydantic import BaseModel


class DisableCommandSchema(BaseModel):
    guild_id: str
    command_name: str