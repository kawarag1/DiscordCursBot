from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status
from typing import Optional

class SessionTokenAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.auto_error = auto_error
    
    async def __call__(self, request: Request) -> Optional[str]:
        session_token = request.cookies.get("session_token")
        
        if not session_token and self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "SessionToken"},
            )
        
        return session_token

def get_swagger_ui_init_oauth(self) -> dict:
        return {
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": "session_token",
        }


session_auth = SessionTokenAuth(auto_error=False)


openapi_scheme = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "session_token",
    "description": "Сессионный токен. Получается при авторизации через Discord и передаётся в cookie или заголовке Authorization: Bearer <token>"
}