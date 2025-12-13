from sqlalchemy import select

from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import User
from app.src.schemas.request.user_update_schema import UserUpdate


class UserRepository(AbstractRepository):
    model = User

    async def get_by_ds_id(self, ds_id: int):
        query = select(self.model).where(self.model.ds_id == ds_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()
        if result:
            return UserUpdate(
                ds_id=result.ds_id,
                avatar_url=result.avatar_url if result.avatar_url else "",
                nickname=result.nickname,
                message_count=result.message_count,
                level=result.level,
            )
        return None
        