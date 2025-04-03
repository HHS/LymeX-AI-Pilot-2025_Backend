from beanie import Document
from typing import Optional

class EmailTemplate(Document):
    template_name: str
    subject: str
    body: str
    from_name: Optional[str]
    from_email: Optional[str]

    class Settings:
        name = "email_templates"
