from fastapi import APIRouter

from .auth import router as auth_router
from .calendar import router as calendar_router
from .admin import router as admin_router
from .tasks import router as tasks_router
from .teams import router as teams_router
from .users import router as user_router

router = APIRouter(prefix="/api")

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(teams_router)
router.include_router(tasks_router)
router.include_router(calendar_router)

router.include_router(admin_router)
