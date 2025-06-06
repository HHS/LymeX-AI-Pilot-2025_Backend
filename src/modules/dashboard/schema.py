from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel

from src.modules.product.feature_status.schema import (
    FeatureStatus,
)


class DashboardProductResponse(BaseModel):
    id: str
    name: str
    is_default: bool
    updated_at: datetime
    regulatory_background_status: FeatureStatus
    claims_builder_status: FeatureStatus
    competitive_analysis_status: FeatureStatus
    standards_guidance_documents_status: FeatureStatus
    performance_testing_requirements_status: FeatureStatus
    regulatory_pathway_analysis_status: FeatureStatus


class DashboardResponse(BaseModel):
    company_id: str
    company_name: str
    products: List[DashboardProductResponse]
