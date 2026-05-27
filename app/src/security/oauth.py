from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.connector import get_session
from app.src.orm.database.repo.owner_repo import OwnerRepository
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.security.jwt_manager import JWTManager
from app.src.utils.logger import logger


async def get_current_owner(
    request: Request, session: AsyncSession = Depends(get_session)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не найден в cookies",
        )
    
    data = await JWTManager().decode_token(token)

    owner_id = data.get("sub")
    if not owner_id:
        logger.critical("Не найден sub (owner_id) в JWT токене!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера, попробуйте позже.",
        )
    owner = await OwnerRepository(session).get_by_id(int(owner_id))
    return OwnerSchema.model_validate(owner)