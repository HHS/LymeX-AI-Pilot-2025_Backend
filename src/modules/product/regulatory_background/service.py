from beanie import PydanticObjectId
from src.modules.product.regulatory_background.model import (
    AnalyzeRegulatoryBackgroundProgress,
    RegulatoryBackground,
)


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


async def get_analyze_regulatory_background_progress(
    product_id: str,
) -> AnalyzeRegulatoryBackgroundProgress | None:
    analyze_regulatory_background_progress = (
        await AnalyzeRegulatoryBackgroundProgress.find_one(
            AnalyzeRegulatoryBackgroundProgress.product_id == str(product_id),
        )
    )
    if not analyze_regulatory_background_progress:
        return None
    return analyze_regulatory_background_progress
