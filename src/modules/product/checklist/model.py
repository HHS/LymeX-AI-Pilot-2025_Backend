from datetime import datetime
from typing import Literal
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.checklist.schema import (
    AnalyzeChecklistProgressResponse,
    ChecklistAnswerResponse,
    ChecklistBase,
    ChecklistResponse,
)
from src.modules.product.models import Product
from src.modules.product.checklist.questions import questions


def question_number_to_module(question_number: str) -> str:
    try:
        question_number_int = int(question_number)
    except ValueError:
        question_number_int = 0

    if question_number_int <= 9:
        return "Product Profile"
    if question_number_int <= 111:
        return "Performance Testing"
    return "Claim Builder"


def question_number_to_section(question_number: str) -> str:
    try:
        question_number_int = int(question_number)
    except ValueError:
        question_number_int = 0

    if question_number_int <= 9:
        return "performance_testing"
    if question_number_int <= 17:
        return "analytical"
    if question_number_int <= 19:
        return "comparison"
    if question_number_int <= 28:
        return "clinical"
    if question_number_int <= 32:
        return "animal_testing"
    if question_number_int <= 46:
        return "emc_safety"
    if question_number_int <= 59:
        return "wireless"
    if question_number_int <= 62:
        return "software"
    if question_number_int <= 78:
        return "cybersecurity"
    if question_number_int <= 85:
        return "interoperability"
    if question_number_int <= 97:
        return "biocompatibility"
    if question_number_int <= 109:
        return "sterility"
    if question_number_int <= 111:
        return "shelf_life"
    return "claim_builder"


def question_number_to_question_type(
    question_number: str,
) -> Literal["checkbox", "radio", "text", "boolean"]:
    try:
        question_number_int = int(question_number) - 1
    except ValueError:
        question_number_int = 0
    if question_number_int >= len(questions):
        return "text"
    return questions[question_number_int]["question_type"]


def question_number_to_options(question_number: str) -> list[str] | None:
    try:
        question_number_int = int(question_number) - 1
    except ValueError:
        question_number_int = 0

    if question_number_int >= len(questions):
        return None
    return questions[question_number_int]["options"]


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

    def to_checklist_response(
        self,
        product: Product,
        analyze_progress: AnalyzeChecklistProgressResponse | None,
    ) -> ChecklistResponse:
        return ChecklistResponse(
            product_id=self.product_id,
            product_name=product.name,
            revision=product.revision,
            created_at=self.created_at,
            analyzing_status=(
                analyze_progress.analyzing_status
                if analyze_progress
                else AnalyzingStatus.PENDING
            ),
            updated_at=self.updated_at,
            answers=[
                ChecklistAnswerResponse(
                    question_number=answer.question_number,
                    question=answer.question,
                    module=question_number_to_module(answer.question_number),
                    section=question_number_to_section(answer.question_number),
                    status=(
                        "Not Completed"
                        if answer.answer == "Not Available"
                        else "Completed"
                    ),
                    answer=answer.answer,
                    question_type=question_number_to_question_type(
                        answer.question_number
                    ),
                    options=question_number_to_options(answer.question_number),
                )
                for answer in self.answers
            ],
        )
