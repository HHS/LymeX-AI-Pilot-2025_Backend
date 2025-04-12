from typing import Annotated
from fastapi import APIRouter, Depends

from src.modules.support.service import create_support_ticket
from src.modules.company.models import Company
from src.modules.authorization.dependencies import (
    RequireCompanyRole,
    get_current_company,
)
from src.modules.authorization.roles import CompanyRoles
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from src.modules.support.schema import CreateSupportTicketRequest


router = APIRouter()


@router.post("/")
async def create_support_ticket_handler(
    payload: CreateSupportTicketRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
) -> None:
    await create_support_ticket(
        payload.issue_description, current_company, current_user
    )
