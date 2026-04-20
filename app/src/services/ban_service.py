from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.repo.log_repo import LogRepository
from app.src.schemas.request.action_schema import BanSchema


class BanService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_ban(self, ban: BanSchema):
        await LogRepository(self.session).create(**ban.model_dump())

    
