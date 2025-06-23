from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class Milestone(BaseModel):
    row: int = Field(..., description="Row number in the timeline")
    start_date: datetime = Field(..., description="Start date of the milestone")
    end_date: datetime = Field(..., description="End date of the milestone")
    name: str = Field(..., description="Name/title of the milestone")


class MilestonePlanningResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    product_name: str = Field(..., description="Name of the product")
    product_code: str = Field(..., description="Code of the product")
    pathway: str = Field(..., description="Recommended regulatory pathway")
    milestones: List[Milestone] = Field(
        ..., description="List of milestones in the timeline"
    )


class SaveMilestonePlanningRequest(BaseModel):
    milestones: List[Milestone] = Field(..., description="List of milestones to save")
