from src.celery.tasks.send_email import send_email_task
from src.environment import environment
from src.infrastructure.security import create_forgot_password_token, create_verify_email_token
from src.modules.user.models import User
from .models import Session


async def create_session(user_id: str, ip_address: str, user_agent: str) -> Session:
    session = Session(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return await session.insert()


def create_verify_email_url(user: User) -> str:
    verify_email_token = create_verify_email_token(user)
    verify_email_url = f"{environment.frontend_url}?token={verify_email_token}"
    return verify_email_url


def create_and_send_verify_email(user: User) -> None:
    verify_email_url = create_verify_email_url(user)
    send_email_task.delay(
        "verify_email",
        {
            "name": f"{user.first_name} {user.last_name}",
            "verify_email_url": verify_email_url,
        },
        user.email,
    )


def create_forgot_password_url(user: User) -> str:
    forgot_password_token = create_forgot_password_token(user)
    forgot_password_url = (
        f"{environment.frontend_url}/forgot-password?token={forgot_password_token}"
    )
    return forgot_password_url


def create_and_send_forgot_password_email(user: User) -> None:
    forgot_password_url = create_forgot_password_url(user)
    send_email_task.delay(
        "forgot_password",
        {
            "name": f"{user.first_name} {user.last_name}",
            "forgot_password_url": forgot_password_url,
        },
        user.email,
    )
