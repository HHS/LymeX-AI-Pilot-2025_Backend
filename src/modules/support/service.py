from src.celery.tasks.send_email import send_email_task
from src.modules.company.service import get_company_administrators
from src.modules.user.models import User
from src.modules.company.models import Company
from src.infrastructure.minio import upload_file
from fastapi import UploadFile
from typing import List
from datetime import datetime
from loguru import logger
from src.environment import environment


async def send_support_confirmation_email(
    user: User,
    issue_type: str,
) -> None:
    logger.info(f"Sending support confirmation email to user: {user.email}")

    send_email_task.delay(
        "support_confirmation",
        {
            "user_name": f"{user.first_name} {user.last_name}",
            "issue_type": issue_type,
        },
        user.email,
    )


async def create_support_ticket(
    issue_description: str,
    company: Company,
    user: User,
) -> None:
    # Send to specific support email instead of company administrators
    support_email = "nois2-192-lymex-support@crowdplat.com"
    send_email_task.delay(
        "support_ticket",
        {
            "user_email": user.email,
            "issue_description": issue_description,
        },
        support_email,
    )


async def create_enhanced_support_ticket(
    issue_type: str,
    description: str,
    attachments: List[UploadFile],
    company: Company,
    user: User,
) -> None:
    # Upload attachments to MinIO
    attachment_object_names = []

    logger.info(f"Processing {len(attachments)} attachments")

    for attachment in attachments:
        # Use original filename for better user experience
        object_name = f"support_attachments/{attachment.filename}"

        # Read file content
        content = await attachment.read()
        logger.info(f"Read {len(content)} bytes from {attachment.filename}")

        # Upload to MinIO
        try:
            await upload_file(
                object_name=object_name,
                file_content=content,
                content_type=attachment.content_type or "application/octet-stream"
            )
            attachment_object_names.append(object_name)
            logger.info(f"Uploaded {attachment.filename} to MinIO: {object_name}")
        except Exception as e:
            logger.error(f"Failed to upload {attachment.filename}: {e}")
            raise

    logger.info(f"All attachment object names: {attachment_object_names}")

    # Send to specific support email
    support_email = "nois2-192-lymex-support@crowdplat.com"

    # Send email with attachments
    logger.info(
        f"Sending email with {len(attachment_object_names)} attachments to {support_email}"
    )
    send_email_task.delay(
        "enhanced_support_ticket",
        {
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name}",
            "company_name": company.name,
            "issue_type": issue_type,
            "description": description or "No description provided",
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "environment": "Production" if environment.is_production else "Development",
        },
        support_email,
        attachments=attachment_object_names,
    )
