from beanie import PydanticObjectId
from src.modules.product.regulatory_background.analyze_regulatory_background_progress import (
    AnalyzeRegulatoryBackgroundProgress,
)
from src.modules.product.regulatory_background.model import RegulatoryBackground


async def get_product_regulatory_backgrounds(
    product_id: str | PydanticObjectId,
) -> list[RegulatoryBackground]:
    product_regulatory_backgrounds = await RegulatoryBackground.find(
        RegulatoryBackground.product_id == str(product_id)
    ).to_list()
    return product_regulatory_backgrounds


async def clone_regulatory_background(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_regulatory_backgrounds = await RegulatoryBackground.find(
        RegulatoryBackground.product_id == str(product_id),
    ).to_list()
    if existing_regulatory_backgrounds:
        await RegulatoryBackground.insert_many(
            [
                RegulatoryBackground(
                    **background.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for background in existing_regulatory_backgrounds
            ]
        )
