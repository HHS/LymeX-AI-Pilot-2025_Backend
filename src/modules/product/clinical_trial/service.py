from beanie import PydanticObjectId
from src.modules.product.clinical_trial.model import ClinicalTrial


async def get_product_clinical_trials(
    product_id: str | PydanticObjectId,
) -> list[ClinicalTrial]:
    product_clinical_trials = await ClinicalTrial.find(
        ClinicalTrial.product_id == str(product_id)
    ).to_list()
    return product_clinical_trials


async def clone_clinical_trial(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    clinical_trials = await ClinicalTrial.find(
        ClinicalTrial.product_id == str(product_id)
    ).to_list()
    if not clinical_trials:
        return
    await ClinicalTrial.insert_many([
        ClinicalTrial(
            **trial.model_dump(exclude={"id", "product_id"}),
            product_id=str(new_product_id),
        )
        for trial in clinical_trials
    ])
