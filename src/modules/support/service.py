from src.celery.tasks.send_email import send_email_task
from src.modules.company.service import get_company_administrators
from src.modules.user.models import User
from src.modules.company.models import Company
from fastapi import UploadFile
from typing import List
from datetime import datetime
from loguru import logger


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


async def create_enhanced_support_ticket(
    issue_type: str,
    description: str,
    attachments: List[UploadFile],
    company: Company,
    user: User,
) -> None:
    # Save attachments to temporary storage
    attachment_paths = []
    
    logger.info(f"Processing {len(attachments)} attachments")
    
    for attachment in attachments:
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"support_{user.id}_{timestamp}_{attachment.filename}"
        
        # Save file to temporary directory
        file_path = f"/tmp/{filename}"
        logger.info(f"Saving attachment to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            content = await attachment.read()
            buffer.write(content)
            logger.info(f"Saved {len(content)} bytes to {file_path}")
        
        attachment_paths.append(file_path)
    
    logger.info(f"All attachment paths: {attachment_paths}")
    
    company_administrators = await get_company_administrators(company)
    to_emails = [user.email for user in company_administrators]
    
    # Send email with attachments
    logger.info(f"Sending email with {len(attachment_paths)} attachments")
    send_email_task.delay(
        "enhanced_support_ticket",
        {
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name}",
            "company_name": company.name,
            "issue_type": issue_type,
            "description": description,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        },
        ", ".join(to_emails),
        attachments=attachment_paths,
    )
