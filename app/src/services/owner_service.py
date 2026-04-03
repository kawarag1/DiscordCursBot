from typing import Any, Dict

import httpx
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.src.orm.database.repo.owner_repo import OwnerRepository
from app.src.settings.settings import settings
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.schemas.response.ds_token_response import DsTokenResponse


class OwnerService:
    def __init__(self, session: AsyncSession):
        self.session = session

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

            return DsTokenResponse(**token_data, session_token=secrets.token_urlsafe(32), expires_at=int((datetime.utcnow() + timedelta(seconds=token_data['expires_in'])).timestamp()))

            
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

    async def add_owner(self, owner_id: int, access_token:str, refresh_token: str, session_token: str, expires_at: int | datetime) -> OwnerSchema:
        if isinstance(expires_at, int):
            expires_at = datetime.fromtimestamp(expires_at, tz=timezone.utc)

        if await OwnerRepository(self.session).exists_by_ds_id(owner_id):
            await OwnerRepository(self.session).update_refresh_token(owner_id, access_token, refresh_token, session_token, expires_at)
            return await OwnerRepository(self.session).get_by_ds_id(owner_id)
        else:
            return await OwnerRepository(self.session).create(ds_id=owner_id, access_token=access_token, refresh_token=refresh_token, session_token=session_token, expires_at=expires_at)

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> DsTokenResponse:
        """Обновление истекшего access_token"""
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
        
    


    