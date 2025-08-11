from typing import TypedDict, List
from loguru import logger
from email.message import EmailMessage
import smtplib
from src.environment import environment
from src.infrastructure.minio import download_file, remove_object
import os


class Email(TypedDict):
    from_email: str
    from_name: str
    subject: str
    body: str


async def send_email(
    email: Email,
    to_email: str,
    cc: list[str] = [],
    bcc: list[str] = [],
    attachments: List[str] = [],
) -> None:
    logger.info(f"Sending email to: {to_email}")
    logger.info(f"Email subject: {email['subject']}")
    logger.info(f"Number of attachments: {len(attachments)}")
    logger.info(f"Attachment object names: {attachments}")

    message = EmailMessage()
    message["From"] = f"{email['from_name']} <{email['from_email']}>"
    message["To"] = to_email
    message["Subject"] = email["subject"]
    message.set_content(email["body"], subtype="html")

    if cc:
        message["Cc"] = ", ".join(cc)
    if bcc:
        message["Bcc"] = ", ".join(bcc)

    # Add attachments from MinIO
    for object_name in attachments:
        logger.info(f"Processing attachment from MinIO: {object_name}")
        try:
            # Download file from MinIO
            file_content = await download_file(object_name)
            filename = os.path.basename(object_name)
            logger.info(f"Downloaded {len(file_content)} bytes from MinIO: {filename}")

            # Add to email
            message.add_attachment(
                file_content,
                maintype="application",
                subtype="octet-stream",
                filename=filename,
            )

            # Clean up the file from MinIO
            try:
                await remove_object(object_name)
                logger.info(f"Removed file from MinIO: {object_name}")
            except Exception as e:
                logger.warning(f"Failed to remove file from MinIO {object_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to process attachment {object_name}: {e}")

    recipients = [to_email] + cc + bcc

    try:
        with smtplib.SMTP(environment.smtp_host, environment.smtp_port) as server:
            server.starttls()
            server.login(environment.smtp_username, environment.smtp_password)
            server.send_message(message, to_addrs=recipients)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise e
