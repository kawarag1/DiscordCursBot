from pydantic import BaseModel, field_serializer


class DisableCommandSchema(BaseModel):
    guild_id: int
    command_name: str

    @field_serializer('guild_id')
    def serialize_guild_id(self, value: int) -> str:
        return str(value)