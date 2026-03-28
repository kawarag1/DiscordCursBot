from typing import Any, Dict

import httpx
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
                settings.token_uri,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get token: {response.text}")
            token_data = response.json()

            return DsTokenResponse(**token_data)

            
    async def get_owner_info(self, access_token: str) -> OwnerSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.user_uri,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {response.text}"
                )
            
            user_data = response.json()
            return OwnerSchema(id=user_data["id"]).model_dump()

    async def add_owner(self, owner_id: int):
        return await OwnerRepository(self.session).create(id=owner_id)
    

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> DsTokenResponse:
        """Обновление истекшего access_token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.token_uri,
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


    