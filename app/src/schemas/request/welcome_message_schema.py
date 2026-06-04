from pydantic import BaseModel

class WelcomeMessageSchema(BaseModel):
    welcome_message: str | None