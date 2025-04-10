from fastapi import APIRouter
from .router_me import router as router_me

router = APIRouter()
router.include_router(
    router_me,
    prefix="/me",
)
