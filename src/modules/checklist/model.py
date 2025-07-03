from datetime import datetime
from typing import List, Literal
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.checklist.schema import ChecklistQuestion, ChecklistProgress


class Checklist(Document):
    product_id: str = Field(..., description="Product ID this checklist belongs to")
    ai_analysis_status: Literal["not_started", "in_progress", "completed"] = Field(
        default="not_started", description="Status of AI analysis"
    )
    checklist: ChecklistProgress = Field(
        ..., description="Checklist progress information"
    )
    questions: List[ChecklistQuestion] = Field(
        ..., description="List of checklist questions"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    class Settings:
        name = "checklist"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def update_progress(self):
        """Update the checklist progress based on completed questions"""
        total = len(self.questions)
        completed = sum(1 for q in self.questions if q.status == "complete")
        self.checklist = ChecklistProgress(total=total, completed=completed)
        self.updated_at = datetime.utcnow()

    def get_questions_by_module(self, module: str) -> List[ChecklistQuestion]:
        """Get all questions for a specific module"""
        return [q for q in self.questions if q.module == module]

    def get_questions_by_status(self, status: str) -> List[ChecklistQuestion]:
        """Get all questions with a specific status"""
        return [q for q in self.questions if q.status == status]

    def get_completion_percentage(self) -> float:
        """Get the completion percentage of the checklist"""
        if self.checklist.total == 0:
            return 0.0
        return (self.checklist.completed / self.checklist.total) * 100
