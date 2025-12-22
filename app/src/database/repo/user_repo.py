from sqlalchemy import select

from app.src.database.repo.abc_repo import AbstractRepository
from app.src.database.models.models import User
from app.src.schemas.request.user_update_schema import UserUpdate


class UserRepository(AbstractRepository):
    model = User

    async def get_by_ds_id(self, ds_id: int):
        query = select(self.model).where(self.model.ds_id == ds_id)
        result = await self._session.execute(query)
        user =  result.scalars().one_or_none()
        return user
        