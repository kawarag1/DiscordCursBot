from datetime import datetime
from fastapi import HTTPException
import jwt

from app.src.schemas.token_payload import TokenPayload
from app.src.security.jwt_params import JWTLifetime, JWTParams
from app.src.security.jwt_type import JWTType
from app.src.settings.settings import settings


class JWTManager:
    def __init__(
        self,
        jwt_config: JWTParams = JWTParams(
            algorithms=[settings.JWT_ALGORITHM],
            secret_key=settings.jwt_secret_key,
            lifetime=JWTLifetime(
                for_access=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES,
                for_refresh=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS,
            ),
        ),
    ):
        self.jwt_config = jwt_config

    async def encode_token(self, payload: TokenPayload, token_type: JWTType = JWTType.ACCESS) -> str:
        expires = (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(minutes=self.jwt_config.lifetime.for_access)
            if token_type == JWTType.ACCESS
            else datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=self.jwt_config.lifetime.for_refresh)
        )

        payload.exp = expires

        return jwt.encode(
            payload=payload.model_dump(exclude_unset=True),
            key=self.jwt_config.secret_key,
            algorithm=self.jwt_config.algorithms[0],
        )

    async def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.jwt_config.secret_key, algorithms=self.jwt_config.algorithms)
        except:
            raise HTTPException(status_code=401, detail="Invalid token")