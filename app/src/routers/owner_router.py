from fastapi import APIRouter, Depends, Response
import redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.request.code import CodeRequest
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.security.oauth import get_current_owner
from app.src.services.owner_service import OwnerService
from app.src.utils.redis.redis_client import get_redis
from app.src.settings.settings import settings

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/get_owner", description="Авторизация владельца", response_model=OwnerSchema)
async def exchange_code(code: CodeRequest, response: Response, session: AsyncSession = Depends(get_session), redis = Depends(get_redis(0))):
    owner_token = await OwnerService(session, redis).exchange_code(code=code.code)
    ds_id = await OwnerService(session, redis).get_owner_info(owner_token.access_token)
    tokens = await OwnerService(session, redis).add_owner(ds_id, owner_token.access_token, owner_token.refresh_token)
    response.set_cookie(key="access_token", value=tokens.access_token, httponly=True, max_age=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES * 60)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, max_age=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS * 24 * 60 * 60)
    return tokens

@router.post("/logout", description="Выход из аккаунта")
async def logout(response: Response, owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session), redis = Depends(get_redis(0))):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    await OwnerService(session, redis).remove_user_tokens(owner.id)
    return {"detail": "Successfully logged out"}

@router.get("/me", description="Получение информации о владельце", response_model=OwnerSchema)
async def get_current_owner_info(owner: OwnerSchema = Depends(get_current_owner)):
    return owner