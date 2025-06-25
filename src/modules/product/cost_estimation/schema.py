from pydantic import BaseModel
from typing import List, Optional


class CostAnalysis(BaseModel):
    base_mdufa_fee: str
    sbd_fee_reduction: str
    estimated_consulting_costs: str
    clinical_trial_costs: str
    total_estimated_cost: str


class Pathway(BaseModel):
    pathway: str
    costAnalysis: CostAnalysis


class CostEstimationResponse(BaseModel):
    product_id: str
    product_name: str
    product_code: str | None
    can_apply_for_sbd: bool
    pathways: List[Pathway]


class SaveCostEstimationRequest(BaseModel):
    pathway: str
    costAnalysis: CostAnalysis
