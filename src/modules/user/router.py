from fastapi import APIRouter
from .router_me import router as router_me
from .router_company import router as router_company
from .router_system_admin import router as router_system_admin

router = APIRouter()
router.include_router(
    router_me,
    prefix="/me",
)
router.include_router(
    router_company,
    prefix="/company",
)
router.include_router(
    router_system_admin,
    prefix="/system-admin",
)
