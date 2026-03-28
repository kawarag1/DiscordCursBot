from pydantic import BaseModel


class OwnerSchema(BaseModel):
    id: int