from typing import Annotated

from fastapi import Depends, HTTPException, Header

from .roles import CompanyMemberStatus, CompanyRoles, COMPANY_ROLES_ORDER
from src.modules.company.models import Company, CompanyMember
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User


async def get_current_company(
    company_id: Annotated[str, Header()],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Company:
    company_member = await CompanyMember.find_one(
        CompanyMember.company_id == company_id,
        CompanyMember.user_id == str(current_user.id),
        CompanyMember.status == CompanyMemberStatus.ACTIVE,
    )
    if not company_member:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )
    company = await Company.get(company_member.company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )
    return company


async def get_current_company_member(
    company_id: Annotated[str, Header()],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CompanyRoles:
    company_member = await CompanyMember.find_one(
        CompanyMember.company_id == company_id,
        CompanyMember.user_id == str(current_user.id),
        CompanyMember.status == CompanyMemberStatus.ACTIVE,
    )
    if not company_member:
        raise HTTPException(
            status_code=404,
            detail="Company member not found or you do not have access to it",
        )
    return company_member


class RequireCompanyRole:
    def __init__(self, role: CompanyRoles):
        self.role = role

    async def __call__(
        self,
        current_company_member: Annotated[
            CompanyMember, Depends(get_current_company_member)
        ],
    ) -> bool:
        print(f"Required role: {self.role}, level: {COMPANY_ROLES_ORDER[self.role]}")
        print(
            f"Current role: {current_company_member.role}, level: {COMPANY_ROLES_ORDER[current_company_member.role]}"
        )
        if (
            current_company_member.status != CompanyMemberStatus.ACTIVE
            or COMPANY_ROLES_ORDER[current_company_member.role]
            > COMPANY_ROLES_ORDER[self.role]
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Only {self.role} can perform this action",
            )
        return True