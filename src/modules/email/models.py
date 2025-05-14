from beanie import Document, Indexed
from typing import Annotated


class EmailTemplate(Document):
    template_name: Annotated[str, Indexed(unique=True)]
    subject: str
    body: str
    from_name: str | None
    from_email: str | None

    class Settings:
        name = "email_templates"
