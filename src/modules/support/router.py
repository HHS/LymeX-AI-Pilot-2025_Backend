from typing import Annotated, List
from fastapi import APIRouter, Depends, UploadFile, File, Form
from loguru import logger

from src.modules.support.service import (
    create_support_ticket,
    create_enhanced_support_ticket,
)
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


@router.post("/report-issue-with-attachments")
async def report_issue_with_attachments_handler(
    issue_type: Annotated[str, Form()],
    description: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
    _: Annotated[bool, Depends(RequireCompanyRole(CompanyRoles.CONTRIBUTOR))],
    attachments: List[UploadFile] = File(default=[]),
) -> None:
    """
    Report an issue with attachments.

    This endpoint accepts:
    - issue_type: string (form field)
    - description: string (form field)
    - attachments: list of files (optional)

    The attachments will be included in the email sent to company administrators.
    """
    logger.info(f"Received {len(attachments)} attachments")
    for i, attachment in enumerate(attachments):
        logger.info(
            f"Attachment {i}: {attachment.filename} ({attachment.content_type})"
        )

    await create_enhanced_support_ticket(
        issue_type=issue_type,
        description=description,
        attachments=attachments,
        company=current_company,
        user=current_user,
    )
