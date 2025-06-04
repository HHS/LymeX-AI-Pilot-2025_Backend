from enum import Enum

from pydantic import BaseModel


class FeatureStatus(str, Enum):
    NOT_STARTED = "NotStarted"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class FeaturesStatusResponse(BaseModel):
    product_id: str
    regulatory_background: FeatureStatus
    claim_builder: FeatureStatus
    competitive_analysis: FeatureStatus
    standard_guidance: FeatureStatus
    performance_testing: FeatureStatus
    regulatory_pathway: FeatureStatus
