import asyncio
from typing import Any
from fastapi import HTTPException
from loguru import logger
from src.infrastructure.email import send_email
from src.modules.email.service import create_email
from src.celery.worker import celery
from src.celery.tasks.base import BaseTask


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.send_email",
)
def send_email_task(
    email_template_name: str,
    data: dict[str, Any],
    to_email: str,
    cc: list[str] = [],
    bcc: list[str] = [],
) -> None:
    logger.info(f"Sending email task: {email_template_name} with data: {data}")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_email_task_async(
                email_template_name,
                data,
                to_email,
                cc,
                bcc,
            )
        )
    except HTTPException as e:
        logger.error(f"Failed to send email: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(500, "Internal Server Error") from e


async def send_email_task_async(
    email_template_name: str,
    data: dict[str, Any],
    to_email: str,
    cc: list[str] = [],
    bcc: list[str] = [],
) -> None:
    email = await create_email(email_template_name, data)
    logger.info(f"Sending email: {email}")
    logger.info(f"to_email: {to_email}")
    send_email(email, to_email, cc, bcc)
    logger.info(f"Email sent successfully: {email_template_name}")
