from beanie import PydanticObjectId
from src.modules.product.regulatory_pathway.model import (
    AnalyzeRegulatoryPathwayProgress,
    RegulatoryPathway,
)


async def get_product_regulatory_pathways(
    product_id: str | PydanticObjectId,
) -> list[RegulatoryPathway]:
    product_regulatory_pathways = await RegulatoryPathway.find(
        RegulatoryPathway.product_id == str(product_id)
    ).to_list()
    return product_regulatory_pathways


async def clone_regulatory_pathway(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_regulatory_pathways = await RegulatoryPathway.find(
        RegulatoryPathway.product_id == str(product_id),
    ).to_list()
    if existing_regulatory_pathways:
        await RegulatoryPathway.insert_many(
            [
                RegulatoryPathway(
                    **pathway.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for pathway in existing_regulatory_pathways
            ]
        )


async def get_analyze_regulatory_pathway_progress(
    product_id: str,
) -> AnalyzeRegulatoryPathwayProgress | None:
    analyze_regulatory_pathway_progress = (
        await AnalyzeRegulatoryPathwayProgress.find_one(
            AnalyzeRegulatoryPathwayProgress.product_id == str(product_id),
        )
    )
    if not analyze_regulatory_pathway_progress:
        return None
    return analyze_regulatory_pathway_progress
