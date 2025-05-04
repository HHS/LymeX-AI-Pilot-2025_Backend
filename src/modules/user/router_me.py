from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from src.modules.user.storage import get_update_user_avatar_url
from .service import hash_password, verify_password
from src.modules.authentication.dependencies import get_current_user, require_totp

from .schemas import (
    UpdateAvatarUrlResponse,
    UserUpdateRequest,
    UserUpdatePasswordRequest,
    UserResponse,
)
from .models import User

router = APIRouter()


# 👤 Get current user
@router.get("/")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return await current_user.to_user_response()


# ✏️ Update profile
@router.put("/")
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    await current_user.save()
    return await current_user.to_user_response()


@router.post("/accept-policy")
async def accept_policy(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    current_user.policy_accepted_at = datetime.now(timezone.utc)
    await current_user.save()
    return None


# 🔒 Change password
@router.put("/password")
async def change_password(
    password_data: UserUpdatePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    current_password_correct = verify_password(
        password_data.current_password,
        current_user.password,
    )
    if not current_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    current_user.password = hash_password(password_data.new_password)
    await current_user.save()
    return None


@router.post("/enable-login-totp")
async def enable_login_totp(
    # _: Annotated[bool, Depends(require_totp)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    current_user.enable_totp = True
    await current_user.save()


@router.post("/disable-login-totp")
async def disable_login_totp(
    # _: Annotated[bool, Depends(require_totp)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    current_user.enable_totp = False
    await current_user.save()


@router.get("/update-avatar-url")
async def get_update_avatar_url(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UpdateAvatarUrlResponse:
    update_avatar_url = await get_update_user_avatar_url(str(current_user.id))
    print("=" * 20)
    print(update_avatar_url)
    return {
        "url": update_avatar_url,
    }
