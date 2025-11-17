from sqlalchemy import select, update
from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import ServerProfile
from app.src.schemas.request.server_user_schema import ServerUserCreate


class UserServerRepository(AbstractRepository):
    model = ServerProfile

    async def get_by_ds_id(self, ds_id: int):
        query = select(self.model).where(self.model.ds_id == ds_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()
        return ServerUserCreate(
            ds_id = result.ds_id,
            server_nickname = result.server_nickname,
            message_count = result.message_count,
            level = result.level
        )