from pydantic import BaseModel

class BanSchema(BaseModel):
    delete_user_messages: bool
    reason: str