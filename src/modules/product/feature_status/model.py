from beanie import Document, PydanticObjectId

from src.modules.product.feature_status.schema import (
    FeatureStatus,
    FeaturesStatusResponse,
)


class FeaturesStatus(Document):
    product_id: str
    regulatory_background: FeatureStatus
    claim_builder: FeatureStatus
    competitive_analysis: FeatureStatus
    standard_guidance: FeatureStatus
    performance_testing: FeatureStatus
    regulatory_pathway: FeatureStatus

    class Settings:
        name = "features_status"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_features_status_response(self) -> FeaturesStatusResponse:
        return FeaturesStatusResponse(
            product_id=self.product_id,
            regulatory_background=self.regulatory_background,
            claim_builder=self.claim_builder,
            competitive_analysis=self.competitive_analysis,
            standard_guidance=self.standard_guidance,
            performance_testing=self.performance_testing,
            regulatory_pathway=self.regulatory_pathway,
        )
