from beanie import PydanticObjectId
from src.modules.product.feature_status.model import FeaturesStatus
from src.modules.product.feature_status.schema import FeatureStatus


async def get_feature_status(product_id: str | PydanticObjectId) -> FeaturesStatus:
    feature_status = await FeaturesStatus.find_one(
        FeaturesStatus.product_id == str(product_id)
    )
    if not feature_status:
        feature_status = FeaturesStatus(
            product_id=str(product_id),
            regulatory_background=FeatureStatus.NOT_STARTED,
            claim_builder=FeatureStatus.NOT_STARTED,
            competitive_analysis=FeatureStatus.NOT_STARTED,
            standard_guidance=FeatureStatus.NOT_STARTED,
            performance_testing=FeatureStatus.NOT_STARTED,
            regulatory_pathway=FeatureStatus.NOT_STARTED,
        )
        await feature_status.insert()
    return feature_status
