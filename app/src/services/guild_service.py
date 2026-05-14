import disnake
import httpx
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.src.schemas.request.action_schema import ActionSchema
from app.src.schemas.response.member_schema import MemberSchema
from app.src.services.action_service import ActionService
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
                if not owner.refresh_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Discord session expired. Please login again."
                    )

                try:
                    new_tokens = await OwnerService.refresh_access_token(owner.refresh_token)
                except HTTPException:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Discord session expired. Please login again."
                    )

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
                    status_code=response.status_code,
                    detail=f"Failed to get guilds from Discord: {response.text}"
                )
            
            return response.json()
        
    async def get_owned_guilds(self, owner: OwnerSchema) -> list[GuildSchema]:
        guilds = await self.get_user_guilds(owner)
        
        owned_guilds: list[GuildSchema] = []
        for guild in guilds:
            if guild.get("owner") == True:
                owned_guilds.append(
                    GuildSchema(
                        id=str(guild.get("id")),
                        name=guild.get("name"),
                        icon_url=(
                            f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png"
                            if guild.get("icon")
                            else None
                        ),
                        approximate_member_count=guild.get("approximate_member_count")
                    )
                )
            
        owned_guilds.sort(key=lambda x: x.name.lower())
        return owned_guilds
    
    async def get_guild_members(self, guild_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.GUILD_MEMBERS_URI.format(guild_id=int(guild_id)),
                headers={"Authorization": f"Bot {settings.TOKEN}"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get guild members from Discord: {response.text}"
                )
            
            return response.json()
    
    async def return_guild_members(self, guild_id: int) -> list[MemberSchema]:
        members_ = await self.get_guild_members(guild_id)

        members: list[MemberSchema] = []

        for member in members_:
            user_data = member.get("user", {})
            if user_data.get("bot"):
                continue
            members.append(MemberSchema(
                id=str(user_data.get("id")),
                username=user_data.get("username"),
                avatar_url=(
                    f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
                    if user_data.get("avatar")
                    else None
                ),
                roles=member.get("roles")
            ))

        return members
            
    async def kick_member(self, guild_id: int, user_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.KICK_URI.format(guild_id=guild_id, user_id=user_id),
                headers={"Authorization": f"Bot {settings.TOKEN}"}
            )

            if response.status_code != 204:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to kick member from Discord: {response.text}"
                )

    async def ban_member(self, guild_id: int, user_id: int, reason: str):
        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.BAN_URI.format(guild_id=guild_id, user_id=user_id),
                headers={"Authorization": f"Bot {settings.TOKEN}",
                         "X-Audit-Log-Reason": reason}
            )

            if response.status_code != 204:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to ban member from Discord: {response.text}"
                )
            
            await ActionService(self.session).log_action(
                ActionSchema(
                    guild_id=guild_id,
                    user_id=user_id,
                    action="ban_with_message_deletion",
                    reason=reason,
                    target_id=user_id,
                    details=f"Причина: {reason}",
                    created_at=datetime.utcnow()
                ))
    
    async def ban_member_with_message_deletion(self, guild_id: int, user_id: int, reason: str):
        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.BAN_URI.format(guild_id=guild_id, user_id=user_id),
                json={"delete_message_seconds": 3 * 24 * 60 * 60},
                headers={"Authorization": f"Bot {settings.TOKEN}",
                         "X-Audit-Log-Reason": reason})

            if response.status_code != 204:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to ban member with message deletion from Discord: {response.text}"
                )
            await ActionService(self.session).log_action(
                ActionSchema(
                    guild_id=guild_id,
                    user_id=user_id,
                    action="ban_with_message_deletion",
                    reason=reason,
                    target_id=user_id,
                    details=f"Заблокирован с удалением сообщений за последние 3 дня. Причина: {reason}",
                    created_at=datetime.utcnow()
                ))