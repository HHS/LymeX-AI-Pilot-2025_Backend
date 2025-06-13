from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.user.service import create_user
from src.modules.user.schemas import (
    AddSystemAdminRequest,
    UserCreateRequest,
    UserResponse,
)
from src.modules.authorization.dependencies import require_system_admin
from src.modules.user.models import User

router = APIRouter()


@router.get("/")
async def get_system_admin_handler(
    _: Annotated[bool, Depends(require_system_admin)],
) -> None:
    system_admins = await User.find(
        User.is_system_admin == True,
    ).to_list()
    return [
        await user.to_user_response(populate_companies=False) for user in system_admins
    ]


@router.post("/add")
async def add_system_admin_handler(
    payload: AddSystemAdminRequest,
    _: Annotated[bool, Depends(require_system_admin)],
) -> None:
    if payload.user_id:
        user = await User.get(payload.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await user.update({"$set": {"is_system_admin": True}})
    if payload.user_ids:
        await User.find(
            User.id.in_(payload.user_ids),
        ).update({"$set": {"is_system_admin": True}})


@router.delete("/remove")
async def remove_system_admin_handler(
    payload: AddSystemAdminRequest,
    _: Annotated[bool, Depends(require_system_admin)],
) -> None:
    if payload.user_id:
        user = await User.get(payload.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await user.update({"$set": {"is_system_admin": False}})
    if payload.user_ids:
        await User.find(
            User.id.in_(payload.user_ids),
        ).update({"$set": {"is_system_admin": False}})


@router.post("/user")
async def create_user_handler(
    payload: UserCreateRequest,
    _: Annotated[bool, Depends(require_system_admin)],
) -> UserResponse:
    email_exist = await User.find_one(
        User.email == payload.email,
    )
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    created_user = await create_user(payload, True)
    return await created_user.to_user_response(
        populate_companies=False,
    )
