from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from src.modules.authorization.roles import CompanyRoles
from src.modules.authentication.dependencies import get_current_user
from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
)
from src.modules.company.models import Company
from src.modules.company.schema import (
    AcceptInvitationRequest,
    CompanyMemberResponse,
    CreateInvitationRequest,
    DeactivateMemberRequest,
    UpdateMemberRoleRequest,
)
from src.modules.company.service import (
    accept_invitation,
    create_invitation,
    deactivate_member,
    get_company_members,
    recover_member,
    update_company_member_role,
)
from src.modules.user.models import User
from src.modules.user.service import get_user_by_email, get_user_by_id


router = APIRouter()


@router.get("/")
async def get_company_member_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> list[CompanyMemberResponse]:
    company_members = await get_company_members(current_company)
    return company_members


@router.post("/invite")
async def create_invitation_handler(
    payload: CreateInvitationRequest,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    # __: Annotated[bool, Depends(require_totp)],
) -> None:
    invited_user = await get_user_by_email(payload.email)
    if not invited_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    await create_invitation(invited_user, current_company)
    return None


@router.post("/accept")
async def accept_invitation_handler(
    payload: AcceptInvitationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    company = await Company.get(payload.company_id)
    await accept_invitation(current_user, company)
    return None


@router.post("/deactivate")
async def deactivate_member_handler(
    payload: DeactivateMemberRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    # __: Annotated[bool, Depends(require_totp)],
) -> None:
    if payload.user_id == str(current_user.id):
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate yourself. You can promote another user to admin and then deactivate you by that account.",
        )
    user_to_deactivate = await get_user_by_id(payload.user_id)
    if not user_to_deactivate:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    await deactivate_member(current_company, user_to_deactivate)
    return None


@router.post("/recover")
async def recover_member_handler(
    payload: DeactivateMemberRequest,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    # __: Annotated[bool, Depends(require_totp)],
) -> None:
    user_to_recover = await get_user_by_id(payload.user_id)
    if not user_to_recover:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    await recover_member(current_company, user_to_recover)
    return None


@router.put("/role")
async def update_company_member_role_handler(
    payload: UpdateMemberRoleRequest,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    # __: Annotated[bool, Depends(require_totp)],
) -> None:
    user_to_update = await get_user_by_id(payload.user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    await update_company_member_role(
        current_company,
        user_to_update,
        payload.role,
    )
    return None
