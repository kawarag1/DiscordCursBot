import disnake
import httpx
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.src.services.owner_service import OwnerService
from app.src.settings.settings import settings
from app.src.orm.database.repo.owner_repo import OwnerRepository
from app.src.orm.models.models import Guild as ModelGuild
from app.src.schemas.response.guild_schema import GuildSchema
from app.src.schemas.response.owner_schema import OwnerSchema

class GuildService():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_guild_by_id(self, guild_id: int):
        query = select(ModelGuild).filter(ModelGuild.id == guild_id)
        result = await self.session.execute(query)
        guild = result.first()
        if guild is not None:
            return True
        return False
    
    async def add_new_guild(self, guild: disnake.Guild):
        new_guild = ModelGuild(
            id = guild.id,
            name = guild.name,
            icon_hash = guild.icon.key if guild.icon else None,
        )
        self.session.add(new_guild)
        await self.session.commit()

    async def get_user_guilds(self, owner: OwnerSchema) -> list:
        

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.GUILDS_URI,
                headers={"Authorization": f"Bearer {owner.access_token}"}
            )

            if response.status_code == 401:
                new_tokens = await OwnerService.refresh_access_token(owner.refresh_token)
                await OwnerRepository(self.session).update_refresh_token(
                    ds_id=owner.ds_id,
                    access_token=new_tokens.access_token,
                    refresh_token=new_tokens.refresh_token,
                    session_token=owner.session_token,
                    expires_at=datetime.fromtimestamp(new_tokens.expires_at, tz=timezone.utc)
                )
                response = await client.get(
                    settings.GUILDS_URI,
                    headers={"Authorization": f"Bearer {new_tokens.access_token}"}
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get guilds: {response.text}"
                )
            
            return response.json()
        
    async def get_owned_guilds(self, owner: OwnerSchema) -> list[GuildSchema]:
        guilds = await self.get_user_guilds(owner)
        
        owned_guilds: list[GuildSchema] = []
        for guild in guilds:
            if guild.get("owner") == True:
                owned_guilds.append(
                    GuildSchema(
                        id=int(guild["id"]),
                        name=guild["name"],
                        icon_url=(
                            f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png"
                            if guild.get("icon")
                            else None
                        ),
                    )
                )
            
        owned_guilds.sort(key=lambda x: x.name.lower())
        return owned_guilds