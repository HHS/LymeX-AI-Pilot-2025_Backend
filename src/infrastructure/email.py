from typing import Optional, TypedDict
from loguru import logger
from email.message import EmailMessage
import smtplib
from src.environment import environment


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
) -> None:
    message = EmailMessage()
    message["From"] = f"{email['from_name']} <{email['from_email']}>"
    message["To"] = to_email
    message["Subject"] = email["subject"]
    message.set_content(email["body"])
    if cc:
        message["Cc"] = ", ".join(cc)
    if bcc:
        message["Bcc"] = ", ".join(bcc)

    recipients = [to_email] + cc + bcc

    try:
        with smtplib.SMTP(environment.smtp_host, environment.smtp_port) as server:
            server.starttls()
            server.login(environment.smtp_username, environment.smtp_password)
            server.send_message(message, to_addrs=recipients)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise e
