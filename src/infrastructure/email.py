from typing import TypedDict, List
from loguru import logger
from email.message import EmailMessage
import smtplib
from src.environment import environment
import os


class Email(TypedDict):
    from_email: str
    from_name: str
    subject: str
    body: str


def send_email(
    email: Email,
    to_email: str,
    cc: list[str] = [],
    bcc: list[str] = [],
    attachments: List[str] = [],
) -> None:
    logger.info(f"Sending email to: {to_email}")
    logger.info(f"Email subject: {email['subject']}")
    logger.info(f"Number of attachments: {len(attachments)}")
    logger.info(f"Attachment paths: {attachments}")
    
    message = EmailMessage()
    message["From"] = f"{email['from_name']} <{email['from_email']}>"
    message["To"] = to_email
    message["Subject"] = email["subject"]
    message.set_content(email["body"], subtype="html")

    if cc:
        message["Cc"] = ", ".join(cc)
    if bcc:
        message["Bcc"] = ", ".join(bcc)

    # Add attachments
    for attachment_path in attachments:
        logger.info(f"Processing attachment: {attachment_path}")
        if os.path.exists(attachment_path):
            logger.info(f"Attachment file exists: {attachment_path}")
            try:
                with open(attachment_path, "rb") as f:
                    file_data = f.read()
                    filename = os.path.basename(attachment_path)
                    logger.info(f"Adding attachment: {filename} ({len(file_data)} bytes)")
                    message.add_attachment(
                        file_data,
                        maintype="application",
                        subtype="octet-stream",
                        filename=filename
                    )
                # Clean up the temporary file
                try:
                    os.remove(attachment_path)
                    logger.info(f"Removed temporary file: {attachment_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {attachment_path}: {e}")
            except Exception as e:
                logger.error(f"Failed to process attachment {attachment_path}: {e}")
        else:
            logger.error(f"Attachment file does not exist: {attachment_path}")

    recipients = [to_email] + cc + bcc

    try:
        with smtplib.SMTP(environment.smtp_host, environment.smtp_port) as server:
            server.starttls()
            server.login(environment.smtp_username, environment.smtp_password)
            server.send_message(message, to_addrs=recipients)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise e
