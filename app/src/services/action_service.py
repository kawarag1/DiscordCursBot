from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.repo.log_repo import LogRepository
from app.src.schemas.request.action_schema import ActionSchema


class ActionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(self, action: ActionSchema):
        await LogRepository(self.session).create(**action.model_dump())

    
