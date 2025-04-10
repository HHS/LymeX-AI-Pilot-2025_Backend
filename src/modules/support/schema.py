from pydantic import BaseModel


class CreateSupportTicketRequest(BaseModel):
    issue_description: str
