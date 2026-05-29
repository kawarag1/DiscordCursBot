from sqlalchemy import delete, select

from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Attachments, Guild, Messages

class GuildsRepository(AbstractRepository):
    model = Guild

    async def delete_message_attachments(self, guild_id: int):
        query = delete(Attachments).where(Attachments.message_id.in_(select(Messages.id).where(Messages.guild_id == guild_id)))
        await self._session.execute(query)

    async def delete_messages(self, guild_id: int):
        query = delete(Messages).where(Messages.guild_id == guild_id)
        await self._session.execute(query)
