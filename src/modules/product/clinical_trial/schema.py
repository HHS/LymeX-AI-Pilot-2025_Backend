from enum import Enum
from pydantic import BaseModel, Field


class ClinicalTrialStatus(str, Enum):
    PLANNED = "planned"
    RECRUITING = "recruiting"
    ACTIVE = "active"
    COMPLETED = "completed"


class ClinicalTrialResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the clinical trial")
    product_id: str = Field(
        ..., description="ID of the product associated with the clinical trial"
    )
    name: str = Field(..., description="Name of the clinical trial")
    sponsor: str = Field(..., description="Sponsor of the clinical trial")
    study_design: str = Field(..., description="Study design of the clinical trial")
    enrollment: int = Field(..., description="Number of participants enrolled")
    status: ClinicalTrialStatus = Field(
        ..., description="Current status of the clinical trial"
    )
    phase: int = Field(..., description="Phase of the clinical trial")
    outcome: str = Field(..., description="Outcome of the clinical trial")
    inclusion_criteria: list[str] = Field(
        ..., description="Inclusion criteria for the clinical trial"
    )
    marked: bool = Field(default=False, description="Whether the trial is marked")
