from typing import Annotated
from fastapi import APIRouter, Depends

from .service import (
    check_user_totp,
    remove_user_totp,
    setup_user_totp,
    verify_user_totp,
)
from .schemas import (
    CheckTOTPRequest,
    CheckTOTPResponse,
    SetupTOTPResponse,
    VerifyTOTPRequest,
)
from src.modules.authentication.dependencies import get_current_user, require_totp
from src.celery.tasks.echo import echo_task
from src.modules.user.models import User
from src.modules.health.service import check_mongo_health

router = APIRouter()


@router.post("/setup")
async def setup_totp(
    current_user: Annotated[User, Depends(get_current_user)],
) -> SetupTOTPResponse:
    provisioning_uri = await setup_user_totp(current_user)
    return SetupTOTPResponse(
        provisioning_uri=provisioning_uri,
    )


@router.post("/verify")
async def verify_totp(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: VerifyTOTPRequest,
) -> None:
    await verify_user_totp(
        current_user,
        payload.code,
    )


@router.post("/check")
async def check_totp(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: CheckTOTPRequest,
) -> CheckTOTPResponse:
    is_totp_valid = await check_user_totp(
        current_user,
        payload.code,
    )
    return CheckTOTPResponse(
        is_valid=is_totp_valid,
    )


@router.post("/remove")
async def remove_totp(
    _: Annotated[None, Depends(require_totp)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await remove_user_totp(current_user)
