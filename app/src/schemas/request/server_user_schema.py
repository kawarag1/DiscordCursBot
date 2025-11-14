from pydantic import BaseModel

class ServerUserCreate(BaseModel):
    ds_id: int
    server_nickname: str
    message_count: int
    level: int