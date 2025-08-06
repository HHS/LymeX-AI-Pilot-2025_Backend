from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.product.checklist.schema import ChecklistBase, ChecklistResponse


class Checklist(Document, ChecklistBase):
    product_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "checklist"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_checklist_response(self) -> ChecklistResponse:
        return ChecklistResponse(
            product_id=self.product_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            answers=self.answers,
        )
