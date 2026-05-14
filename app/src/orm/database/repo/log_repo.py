from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Log_entries

class LogRepository(AbstractRepository):
    model = Log_entries

    async def get_by_guild_id(self, guild_id: int):
        query = self._session.select(self.model).filter_by(guild_id=guild_id)
        result = await self._session.execute(query)
        return result.scalars().all()