from typing import List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ChecklistQuestion(BaseModel):
    id: str = Field(..., description="Unique identifier for the question")
    question: str = Field(..., description="The actual question text")
    status: Literal["complete", "incomplete", "N/A"] = Field(..., description="Status of the question")
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


class ChecklistProgress(BaseModel):
    total: int = Field(..., description="Total number of checklist items")
    completed: int = Field(..., description="Number of completed checklist items")


class ChecklistData(BaseModel):
    product_id: str = Field(..., description="Product ID this checklist belongs to")
    ai_analysis_status: Literal["not_started", "in_progress", "completed"] = Field(
        default="not_started", 
        description="Status of AI analysis"
    )
    checklist: ChecklistProgress = Field(..., description="Checklist progress information")
    questions: List[ChecklistQuestion] = Field(..., description="List of checklist questions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


# Request/Response schemas
class ChecklistCreateRequest(BaseModel):
    product_id: str = Field(..., description="Product ID for the checklist")
    questions: List[ChecklistQuestion] = Field(..., description="List of questions to create")


class ChecklistUpdateRequest(BaseModel):
    ai_analysis_status: Literal["not_started", "in_progress", "completed"] | None = None
    questions: List[ChecklistQuestion] | None = None


class ChecklistResponse(BaseModel):
    id: str = Field(..., description="Checklist ID")
    product_id: str = Field(..., description="Product ID")
    ai_analysis_status: Literal["not_started", "in_progress", "completed"]
    checklist: ChecklistProgress
    questions: List[ChecklistQuestion]
    created_at: datetime
    updated_at: datetime


class ChecklistListResponse(BaseModel):
    checklists: List[ChecklistResponse] = Field(..., description="List of checklists")
    total: int = Field(..., description="Total number of checklists")
