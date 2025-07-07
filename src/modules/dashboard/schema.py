from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product.feature_status.schema import (
    FeatureStatus,
)


class DashboardProductResponse(BaseModel):
    id: str
    name: str
    is_default: bool
    updated_at: datetime
    regulatory_background_percentage: float = Field(default=0.0, ge=0, le=100)
    claims_builder_percentage: float = Field(default=0.0, ge=0, le=100)
    competitive_analysis_percentage: float = Field(default=0.0, ge=0, le=100)
    standards_guidance_documents_percentage: float = Field(default=0.0, ge=0, le=100)
    performance_testing_requirements_percentage: float = Field(
        default=0.0, ge=0, le=100
    )
    regulatory_pathway_analysis_percentage: float = Field(default=0.0, ge=0, le=100)
    remaining_tasks: int = Field(
        default=0, ge=0, description="Number of remaining tasks"
    )


class ProductListResponse(BaseModel):
    id: str
    name: str
    code: str
    model: str
    revision: str
    category: str
    is_default: bool
    updated_at: datetime
    remaining_tasks: int = Field(
        default=0, ge=0, description="Number of remaining tasks"
    )


class DashboardResponse(BaseModel):
    company_id: str
    company_name: str
    products: List[DashboardProductResponse]
