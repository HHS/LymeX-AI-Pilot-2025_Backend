from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class ChecklistAnswer(BaseModel):
    question_number: str
    question: str
    answer: str


class ChecklistBase:
    answers: list[ChecklistAnswer]


class ChecklistResponse(BaseModel, ChecklistBase):
    product_id: str
    created_at: datetime
    updated_at: datetime | None


class AnalyzeChecklistProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )
