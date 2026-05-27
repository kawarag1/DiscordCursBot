from typing import Optional
from pydantic import BaseModel, ConfigDict


class OwnerSchema(BaseModel):
    id: int
    ds_id: int
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)