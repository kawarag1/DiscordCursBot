from sqlalchemy.ext.asyncio import AsyncSession
from app.src.orm.database.repo.user_server_repo import UserServerRepository
from app.src.schemas.request.server_user_schema import ServerUserCreate

class ServerProfileService():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_new_server_profile(self, user: ServerUserCreate):
        await UserServerRepository(self.session).create(**user.model_dump())

    async def delete_server_profile(self, ds_id: int):
        await UserServerRepository(self.session).delete_by_DSid(ds_id)