from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product.product_profile.schema import AnalyzingStatus


class AlternativePathway(BaseModel):
    name: str
    confident_score: int


class RegulatoryPathwayJustification(BaseModel):
    title: str
    content: str


# ================= RESPONSES =================


class RegulatoryPathwayResponse(BaseModel):
    product_id: str = Field(..., description="Unique identifier for the product")
    recommended_pathway: str = Field(..., description="Recommended regulatory pathway")
    confident_score: int = Field(
        ..., description="Confidence score for the recommendation"
    )
    description: str = Field(..., description="Description of the recommended pathway")
    estimated_time_days: int = Field(
        ..., description="Estimated time in days for the pathway"
    )
    alternative_pathways: list[AlternativePathway] = Field(
        ..., description="List of alternative regulatory pathways"
    )
    justifications: list[RegulatoryPathwayJustification] = Field(
        ..., description="List of justifications for the recommendation"
    )
    supporting_documents: list[str] = Field(
        ..., description="List of supporting document URLs or identifiers"
    )


class AnalyzeRegulatoryPathwayProgressResponse(BaseModel):
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
