from beanie import Document, PydanticObjectId
from typing import List
from datetime import datetime

from src.modules.product.milestone_planning.schema import (
    Milestone,
    MilestonePlanningResponse,
)
from src.modules.product.models import Product  # Add this import


class MilestonePlanning(Document):
    product_id: str
    milestones: List[Milestone]

    class Settings:
        name = "milestone_planning"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_milestone_planning_response(self) -> MilestonePlanningResponse:
        # Fetch the product to get its name
        product = await Product.get(self.product_id)
        return MilestonePlanningResponse(
            product_id=self.product_id,
            product_name=product.name,
            milestones=self.milestones,
        )
