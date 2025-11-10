from pydantic import BaseModel

class UserForDelete(BaseModel):
    ds_id: int