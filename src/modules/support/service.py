from src.celery.tasks.send_email import send_email_task
from src.modules.company.service import get_company_administrators
from src.modules.user.models import User
from src.modules.company.models import Company


async def create_support_ticket(
    issue_description: str,
    company: Company,
    user: User,
) -> None:
    company_administrators = await get_company_administrators(company)
    to_emails = [user.email for user in company_administrators]
    send_email_task.delay(
        "support_ticket",
        {
            "user_email": user.email,
            "issue_description": issue_description,
        },
        ", ".join(to_emails),
    )
