from typing import List, Literal
from pydantic import BaseModel, Field


class MasterChecklistQuestion(BaseModel):
    question: str = Field(..., description="The actual question text")
    module: Literal[
        "Product Profile",
        "Claims Builder",
        "Competitive Analysis",
        "Clinical Trial",
        "Performance Testing",
        "Regulatory Pathway",
        "Cost Estimation",
    ] = Field(..., description="Module the question belongs to")
    draft: bool = Field(..., description="Whether the question is in draft mode")
    is_yes_or_no_question: bool = Field(
        ..., description="Whether this is a yes/no question"
    )
    default_answer: str = Field(
        default="", description="Default answer for the question"
    )


# Schema for the JSON file structure (array of questions)
class MasterChecklistData(BaseModel):
    questions: List[MasterChecklistQuestion] = Field(
        ..., description="List of template questions"
    )
