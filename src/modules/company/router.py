from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from beanie.operators import Set

from src.modules.company.storage import get_update_company_logo_url

from .router_member import router as member_router

from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
    get_current_company_member,
    RequireCompanyRole,
    require_system_admin,
)
from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles
from src.modules.company.schema import (
    AddCompanyAdminRequest,
    CompanyMemberResponse,
    CompanyResponse,
    CompanyRoleResponse,
    CreateCompanyRequest,
    UpdateCompanyLogoResponse,
    UpdateCompanyRequest,
)
from src.modules.company.service import (
    create_company,
    get_companies,
    get_company_members,
)
from src.modules.company.models import Company, CompanyMember
from src.modules.user.models import User
from src.modules.authentication.dependencies import get_current_user, require_totp

router = APIRouter()

router.include_router(
    member_router,
    prefix="/member",
)


@router.get("/list")
async def get_companies_handler(
    current_user: Annotated[User, Depends(get_current_user)],
    status: CompanyMemberStatus = CompanyMemberStatus.ACTIVE,
) -> list[CompanyResponse]:
    companies = await get_companies(current_user, status)
    return [await company.to_company_response() for company in companies]


@router.post("/")
async def create_company_handler(
    payload: CreateCompanyRequest,
    _: Annotated[User, Depends(require_system_admin)],
) -> CompanyResponse:
    created_company = await create_company(payload)
    return await created_company.to_company_response()


@router.get("/company-admin")
async def get_company_admins_handler(
    company_id: str,
    _: Annotated[User, Depends(require_system_admin)],
) -> list[CompanyMemberResponse]:
    company = await Company.get(company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )
    company_members = await get_company_members(company)
    company_admins = [
        company_member
        for company_member in company_members
        if company_member.role == CompanyRoles.ADMINISTRATOR
    ]
    return company_admins


@router.post("/add-company-admin")
async def add_company_admin_handler(
    payload: AddCompanyAdminRequest,
    _: Annotated[User, Depends(require_system_admin)],
) -> None:
    user = await User.get(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    company = await Company.get(payload.company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )
    company_member = await CompanyMember.find_one(
        CompanyMember.user_id == payload.user_id,
        CompanyMember.company_id == payload.company_id,
    )
    if not company_member:
        company_member = CompanyMember(
            user_id=payload.user_id,
            company_id=payload.company_id,
            role=CompanyRoles.ADMINISTRATOR,
            status=CompanyMemberStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
        )
        await company_member.insert()
    else:
        company_member.role = CompanyRoles.ADMINISTRATOR
        company_member.status = CompanyMemberStatus.ACTIVE
        await company_member.save()


@router.delete("/remove-company-admin")
async def remove_company_admin_handler(
    payload: AddCompanyAdminRequest,
    _: Annotated[User, Depends(require_system_admin)],
) -> None:
    user = await User.get(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    company = await Company.get(payload.company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )
    company_member = await CompanyMember.find_one(
        CompanyMember.user_id == payload.user_id,
        CompanyMember.company_id == payload.company_id,
    )
    if not company_member:
        raise HTTPException(
            status_code=404,
            detail="Company member not found",
        )
    await company_member.delete()
    return None


@router.get("/")
async def get_company_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
) -> CompanyResponse:
    return await current_company.to_company_response()


@router.get("/role")
async def get_company_role_handler(
    current_company_member: Annotated[
        CompanyMember, Depends(get_current_company_member)
    ],
) -> CompanyRoleResponse:
    return current_company_member.to_company_role_response()


@router.put("/")
async def update_company_handler(
    payload: UpdateCompanyRequest,
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
) -> CompanyResponse:
    await current_company.update(Set(payload.model_dump(exclude_unset=True)))
    return await current_company.to_company_response()


@router.delete("/")
async def delete_company_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    # __: Annotated[bool, Depends(require_totp)],
) -> None:
    current_company.deleted_at = datetime.now(timezone.utc)
    await current_company.save()
    return None


@router.post("/recover")
async def recover_company_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.ADMINISTRATOR))],
    # __: Annotated[bool, Depends(require_totp)],
) -> None:
    current_company.deleted_at = None
    await current_company.save()
    return None


@router.get("/update-logo-url")
async def get_update_logo_url_handler(
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> UpdateCompanyLogoResponse:
    update_avatar_url = await get_update_company_logo_url(str(current_company.id))
    return {
        "url": update_avatar_url,
    }
