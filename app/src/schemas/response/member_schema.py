from pydantic import BaseModel

class MemberSchema(BaseModel):
    id: str
    username: str
    avatar_url: str | None
    roles: list[int] | None