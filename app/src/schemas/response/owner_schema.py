from pydantic import BaseModel


class OwnerSchema(BaseModel):
    ds_id: int
    refresh_token: str