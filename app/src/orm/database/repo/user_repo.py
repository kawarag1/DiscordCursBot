from sqlalchemy import select
from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import User
from app.src.schemas.request.user_schema import UserCreate


class UserRepository(AbstractRepository):
    model = User

    async def get_by_ds_id(self, ds_id: int):
        query = select(self.model).where(self.model.ds_id == ds_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()
        user = UserCreate(
            ds_id = result.ds_id,
            avatar_url = result.avatar_url if result.avatar_url else "",
            created_at = result.created_at,
            nickname = result.nickname,
            message_count = result.message_count,
            level = result.level,
            guild_id = result.guild_id
        )
        return user
        