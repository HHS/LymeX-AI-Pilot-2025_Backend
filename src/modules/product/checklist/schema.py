from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class ChecklistAnswer(BaseModel):
    question_number: str
    question: str
    answer: str


class ChecklistBase:
    answers: list[ChecklistAnswer]


class ChecklistAnswerResponse(BaseModel):
    question_number: str
    question: str
    module: str
    section: str
    status: Literal["Completed"]
    answer: str
    question_type: Literal["checkbox", "radio", "text", "boolean"]
    options: list[str] | None


class ChecklistResponse(BaseModel):
    product_id: str
    product_name: str
    revision: str
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )
    created_at: datetime
    updated_at: datetime | None
    answers: list[ChecklistAnswerResponse]


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
