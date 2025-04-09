from typing import Any
from src.modules.email.renderer import render_template
from src.infrastructure.email import Email
from .models import EmailTemplate
from fastapi import HTTPException


async def get_template_by_name(template_name: str) -> EmailTemplate:
    template = await EmailTemplate.find_one(
        EmailTemplate.template_name == template_name
    )
    if not template:
        raise HTTPException(404, f"Email template '{template_name}' not found")
    return template


async def create_email(email_template_name: str, data: dict[str, Any]) -> Email:
    template = await get_template_by_name(email_template_name)
    email = Email(
        subject=render_template(template.subject, data),
        body=render_template(template.body, data),
        from_name=render_template(template.from_name, data),
        from_email=render_template(template.from_email, data),
    )
    return email
