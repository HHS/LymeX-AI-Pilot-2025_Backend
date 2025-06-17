from datetime import datetime
from beanie import Document, PydanticObjectId
from typing import List
from src.modules.product.cost_estimation.schema import Pathway, CostEstimationResponse

class CostEstimation(Document):
    product_id: str
    can_apply_for_sbd: bool
    pathways: List[Pathway]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "cost_estimation"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_cost_estimation_response(self) -> "CostEstimationResponse":
        return CostEstimationResponse(
            product_id=self.product_id,
            can_apply_for_sbd=self.can_apply_for_sbd,
            pathways=self.pathways
        )