from fastapi import APIRouter

from app.src.routers.command_router import router as command_router
from app.src.routers.owner_router import router as owner_router
from app.src.routers.guilds_router import router as guilds_router
from app.src.routers.action_router import router as action_router


router = APIRouter(
    prefix="/v1",
)

router.include_router(command_router)
router.include_router(owner_router)
router.include_router(guilds_router)
router.include_router(action_router)
