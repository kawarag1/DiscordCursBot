from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import disnake

from app.src.orm.models.models import Guild as ModelGuild

class GuildService():
    def __init__(self, session: AsyncSession):
        self._session = session

    async def check_guild_by_id(self, guild_id):
        query = select(ModelGuild).where(ModelGuild.id == guild_id)
        result = await self._session.execute(query)
        guild = result.one_or_none()
        return True if not guild else False
    
    async def add_new_guild(self, guild: disnake.Guild):
        result = await self._session.execute(insert(ModelGuild).values(id=guild.id, name=guild.name))
        await self.session.commit()
