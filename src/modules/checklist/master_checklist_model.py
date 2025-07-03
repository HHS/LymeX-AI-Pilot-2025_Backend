from datetime import datetime
from typing import List, Literal
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.checklist.master_checklist_schema import MasterChecklistQuestion
from src.modules.checklist.schema import ChecklistQuestion

class MasterChecklist(Document):
    question: str = Field(..., description="The actual question text")
    module: Literal[
        "Product Profile", 
        "Claims Builder", 
        "Competitive Analysis", 
        "Clinical Trial", 
        "Performance Testing", 
        "Regulatory Pathway", 
        "Cost Estimation"
    ] = Field(..., description="Module the question belongs to")
    draft: bool = Field(..., description="Whether the question is in draft mode")
    is_yes_or_no_question: bool = Field(..., description="Whether this is a yes/no question")
    default_answer: str = Field(default="", description="Default answer for the question")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Settings:
        name = "master_checklist"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    @classmethod
    async def create_from_json_data(cls, json_data: List[dict]) -> List["MasterChecklist"]:
        """Create master checklist records from JSON data (array of questions)"""
        master_checklist_records = []
        for question_data in json_data:
            # Validate the JSON data using the schema
            validated_question = MasterChecklistQuestion(**question_data)
            master_record = cls(
                question=validated_question.question,
                module=validated_question.module,
                draft=validated_question.draft,
                is_yes_or_no_question=validated_question.is_yes_or_no_question,
                default_answer=validated_question.default_answer
            )
            master_checklist_records.append(master_record)
        
        return master_checklist_records

    def create_checklist_question(self, product_id: str, question_index: int) -> ChecklistQuestion:
        """Create a checklist question from this master checklist record"""
        return ChecklistQuestion(
            id=f"{product_id}_q_{question_index+1}",  # Generate unique ID
            question=self.question,
            status="incomplete",  # Default status
            module=self.module,
            draft=self.draft,
            is_yes_or_no_question=self.is_yes_or_no_question,
            default_answer=self.default_answer
        )
