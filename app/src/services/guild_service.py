from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import disnake

from app.src.orm.models.models import Guild as ModelGuild

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