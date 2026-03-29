from fastapi import APIRouter, Depends
from fastapi.params import Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.services.owner_service import OwnerService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/get_owner", description="Авторизация владельца", response_model=OwnerSchema)
async def exchange_code(code: str = Body(...), session: AsyncSession = Depends(get_session)):
    owner_id = await OwnerService(session).exchange_code(code=code)
    owner_info = await OwnerService(session).get_owner_info(owner_id.access_token)
    return await OwnerService(session).add_owner(owner_info.id)
