from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends
from beanie.operators import Set

from src.modules.company.storage import get_update_company_logo_url

from .router_member import router as member_router

from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
    get_current_company_member,
    RequireCompanyRole,
)
from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles
from src.modules.company.schema import (
    CompanyResponse,
    CompanyRoleResponse,
    CreateCompanyRequest,
    UpdateCompanyLogoResponse,
    UpdateCompanyRequest,
)
from src.modules.company.service import (
    create_company,
    get_companies,
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
    current_user: Annotated[User, Depends(get_current_user)],
) -> CompanyResponse:
    created_company = await create_company(payload, current_user)
    return await created_company.to_company_response()


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
    update_avatar_url = await get_update_company_logo_url(current_company)
    return {
        "url": update_avatar_url,
    }
