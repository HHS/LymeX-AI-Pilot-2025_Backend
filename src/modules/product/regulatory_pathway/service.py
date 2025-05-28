from beanie import PydanticObjectId
from src.modules.product.regulatory_pathway.model import RegulatoryPathway


async def get_product_regulatory_pathways(
    product_id: str | PydanticObjectId,
) -> list[RegulatoryPathway]:
    product_regulatory_pathways = await RegulatoryPathway.find(
        RegulatoryPathway.product_id == str(product_id)
    ).to_list()
    return product_regulatory_pathways
