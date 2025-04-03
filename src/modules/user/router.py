from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from .service import hash_password, verify_password
from src.infrastructure.authentication import get_current_user

from .schemas import (
    UserUpdateRequest,
    UserUpdatePasswordRequest,
    UserResponse,
)
from .models import User

router = APIRouter()


# 👤 Get current user
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user.to_user_response()


# ✏️ Update profile
@router.put("/me")
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    await current_user.save()
    return current_user.to_user_response


@router.post("/me/accept-policy")
async def accept_policy(
    current_user: User = Depends(get_current_user),
) -> None:
    current_user.policy_accepted_at = datetime.now(timezone.utc)
    await current_user.save()
    return None


# 🔒 Change password
@router.put("/me/password")
async def change_password(
    password_data: UserUpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
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
