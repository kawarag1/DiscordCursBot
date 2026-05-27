import httpx
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.src.orm.database.repo.owner_repo import OwnerRepository
from app.src.schemas.response.access_token import AccessToken
from app.src.schemas.token_payload import TokenPayload
from app.src.security.jwt_manager import JWTManager
from app.src.security.jwt_type import JWTType
from app.src.settings.settings import settings
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.schemas.response.ds_token_response import DsTokenResponse
from app.src.utils.redis.redis_client import AsyncRedisClient


class OwnerService:
    def __init__(self, session: AsyncSession,  redis: AsyncRedisClient | None = None):
        self.session = session
        self._redis = redis

    async def exchange_code(self, code: str):
        data ={
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.REDIRECT_URI
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.TOKEN_URI,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get token: {response.text}")
            token_data = response.json()

            return DsTokenResponse(**token_data)

            
    async def get_owner_info(self, access_token: str) -> int:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.USER_URI,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {response.text}"
                )
            
            user_data = response.json()
            return int(user_data["id"])


    async def get_user_tokens(self, **kwargs)-> AccessToken | None:
        token_payload = TokenPayload(**kwargs)
        jwt_manager = JWTManager()

        return AccessToken(
            access_token=await jwt_manager.encode_token(token_payload, token_type=JWTType.ACCESS),
            refresh_token=await jwt_manager.encode_token(token_payload, token_type=JWTType.REFRESH)
        )
    
    async def store_user_tokens(self, owner_id: int, discord_access_token: str, discord_refresh_token: str):
        await self._redis.check_user_tokens(
            owner_id,
            discord_access_token,
            settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES * 60
        )

        await self._redis.store_refresh_token(
            owner_id,
            discord_refresh_token,
            settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS * 24 * 60 * 60
        )

    async def add_owner(self, owner_id: int, discord_access_token: str, discord_refresh_token: str) -> AccessToken:
        owner = await OwnerRepository(self.session).get_by_ds_id(owner_id)
        if owner:
            await self._redis.revoke_all_user_tokens(owner_id)
            await self.store_user_tokens(owner.id, discord_access_token, discord_refresh_token)
            return await self.get_user_tokens(sub=str(owner.id))
        else:
            owner = await OwnerRepository(self.session).create(ds_id=owner_id)
            await self.store_user_tokens(owner.id, discord_access_token, discord_refresh_token)
            return await self.get_user_tokens(sub=str(owner.id))

    async def get_discord_tokens_from_redis(self, owner_id: int) -> AccessToken | None:
        return await self._redis.get_user_tokens(owner_id)

    async def remove_user_tokens(self, owner_id: int):
        await self._redis.revoke_all_user_tokens(owner_id)

    async def refresh_tokens(self, owner_id: int) -> AccessToken:
        tokens = await self.get_discord_tokens_from_redis(owner_id)
        if not tokens:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tokens found for user")

        new_ds_tokens = await self.refresh_access_token(tokens.refresh_token)
        new_tokens = await self.get_user_tokens(sub=str(owner_id))
        await self.store_user_tokens(owner_id, new_ds_tokens.access_token, new_ds_tokens.refresh_token)
        return new_tokens

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> DsTokenResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.TOKEN_URI,
                data={
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to refresh token"
                )
            
            token_data = response.json()
            return DsTokenResponse(**token_data)

    

    