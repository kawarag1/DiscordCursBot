from fastapi import APIRouter, Depends, Request, Response
from fastapi.params import Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.request.code import CodeRequest
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.security.session_auth_token import session_auth
from app.src.security.oauth import get_current_owner
from app.src.services.owner_service import OwnerService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/get_owner", description="Авторизация владельца", response_model=OwnerSchema)
async def exchange_code(code: CodeRequest, response: Response, session: AsyncSession = Depends(get_session)):
    owner_token = await OwnerService(session).exchange_code(code=code.code)
    ds_id = await OwnerService(session).get_owner_info(owner_token.access_token)
    response.set_cookie(
        key="session_token",
        value=owner_token.session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=owner_token.expires_in)
    return await OwnerService(session).add_owner(ds_id, owner_token.access_token, owner_token.refresh_token, owner_token.session_token, owner_token.expires_at)

@router.post("/logout", dependencies=[Depends(session_auth)], description="Выход из аккаунта")
async def logout(response: Response, owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    response.delete_cookie("session_token")
    return {"detail": "Successfully logged out"}

@router.post("/refresh_session_token", dependencies=[Depends(session_auth)],description="Обновление сессионного токена", response_model=OwnerSchema)
async def refresh_session_token(response: Response, owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    owner_ = await OwnerService(session).refresh_session_token(session_token=owner.session_token)
    response.set_cookie(
        key="session_token",
        value=owner_.session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=owner_.expires_at)
    return owner_

@router.get("/me", dependencies=[Depends(session_auth)], description="Получение информации о владельце", response_model=OwnerSchema)
async def get_current_owner_info(owner: OwnerSchema = Depends(get_current_owner)):
    return owner