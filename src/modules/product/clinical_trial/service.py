from beanie import PydanticObjectId
from src.modules.product.clinical_trial.model import ClinicalTrial


async def get_product_clinical_trials(
    product_id: str | PydanticObjectId,
) -> list[ClinicalTrial]:
    product_clinical_trials = await ClinicalTrial.find(
        ClinicalTrial.product_id == str(product_id)
    ).to_list()
    return product_clinical_trials
