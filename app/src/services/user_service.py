from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.repo.user_repo import UserRepository
from app.src.schemas.request.user_schema import UserCreate


class UserService():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_new_user(self, user: UserCreate):
        await UserRepository(self.session).create(**user.model_dump())

    async def delete_user(self, ds_id: int):
        await UserRepository(self.session).delete_by_DSid(ds_id)

    async def get_server_profile(self, ds_id: int):
        return await UserRepository(self.session).get_by_ds_id(ds_id)

    async def change_server_profile(self, user: UserCreate):
        await UserRepository(self.session).update_by_ds_id(user.ds_id, **user.model_dump())
