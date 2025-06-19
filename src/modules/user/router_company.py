from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, status

from src.modules.user.models import User
from src.modules.company.models import Company, CompanyMember
from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
)
from src.modules.authorization.roles import CompanyRoles

from .schemas import CompanyAdminUpdateUserRequest

router = APIRouter()


@router.patch("/{user_id}")
async def update_user_handler(
    user_id: str,
    payload: CompanyAdminUpdateUserRequest,
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    current_company: Annotated[Company, Depends(get_current_company)],
) -> None:
    existing_member = await CompanyMember.find_one(
        CompanyMember.company_id == str(current_company.id),
        CompanyMember.user_id == user_id,
    )
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company member not found or you do not have access to it",
        )
    if payload.first_name or payload.last_name or payload.email:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if payload.first_name:
            user.first_name = payload.first_name
        if payload.last_name:
            user.last_name = payload.last_name
        if payload.email:
            user.email = payload.email
        await user.save()
    if payload.role or payload.status:
        if payload.role:
            existing_member.role = payload.role
        if payload.status:
            existing_member.status = payload.status
        await existing_member.save()
    return None
