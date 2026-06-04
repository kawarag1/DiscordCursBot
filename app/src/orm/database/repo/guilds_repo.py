from sqlalchemy import delete, select

from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Attachments, Guild, Messages
from app.src.schemas.request.welcome_message_schema import WelcomeMessageSchema

class GuildsRepository(AbstractRepository):
    model = Guild

    async def delete_message_attachments(self, guild_id: int):
        query = delete(Attachments).where(Attachments.message_id.in_(select(Messages.id).where(Messages.guild_id == guild_id)))
        await self._session.execute(query)

    async def delete_messages(self, guild_id: int):
        query = delete(Messages).where(Messages.guild_id == guild_id)
        await self._session.execute(query)
    
    async def get_welcome_message(self, guild_id: int) -> str | None:
        query = select(Guild.welcome_message).where(Guild.id == guild_id)
        result = await self._session.execute(query)
        welcome_message = result.scalar_one_or_none()
        return welcome_message

    async def update_welcome_message(self, guild_id: int, welcome_message: WelcomeMessageSchema):
        query = select(Guild).where(Guild.id == guild_id)
        result = await self._session.execute(query)
        guild = result.scalar_one_or_none()
        if guild:
            guild.welcome_message = welcome_message.welcome_message
            await self._session.commit()