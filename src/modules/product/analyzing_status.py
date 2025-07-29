from enum import Enum

from pydantic import BaseModel, Field


class AnalyzingStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class AnalyzingStatusResponse(BaseModel):
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )
