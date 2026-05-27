from typing import Optional
from pydantic import BaseModel


class OwnerSchema(BaseModel):
    id: int
    ds_id: int
    email: Optional[str]