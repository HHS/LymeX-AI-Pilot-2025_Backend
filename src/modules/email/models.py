from beanie import Document, Indexed
from typing import Annotated, Optional


class EmailTemplate(Document):
    template_name: Annotated[str, Indexed(unique=True)]
    subject: str
    body: str
    from_name: Optional[str]
    from_email: Optional[str]

    class Settings:
        name = "email_templates"
