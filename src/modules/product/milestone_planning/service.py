from beanie import PydanticObjectId
from typing import List
from src.modules.product.milestone_planning.model import MilestonePlanning
from src.modules.product.milestone_planning.schema import Milestone


async def get_product_milestone_planning(
    product_id: str | PydanticObjectId,
) -> list[MilestonePlanning]:
    product_milestone_plannings = await MilestonePlanning.find(
        {"product_id": str(product_id)}
    ).to_list()
    return product_milestone_plannings


async def save_milestone_planning(
    product_id: str | PydanticObjectId,
    milestones: List[Milestone],
) -> MilestonePlanning:
    # Find existing milestone planning
    milestone_planning = await MilestonePlanning.find_one(
        MilestonePlanning.product_id == str(product_id)
    )
    
    if not milestone_planning:
        # If no existing record, create a new one
        milestone_planning = MilestonePlanning(
            product_id=str(product_id),
            milestones=milestones,
        )
    else:
        # Update existing record
        milestone_planning.milestones = milestones
    
    # Save the changes
    await milestone_planning.save()
    
    return milestone_planning