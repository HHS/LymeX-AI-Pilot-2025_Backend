from typing import Annotated, List
from fastapi import APIRouter, Depends
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.models import Product
from src.modules.product.dependencies import get_current_product
from src.modules.product.cost_estimation.service import (
    get_product_cost_estimation,
    save_product_cost_estimation,
)
from src.modules.product.cost_estimation.schema import (
    CostEstimationResponse,
    SaveCostEstimationRequest,
)
from src.modules.product.product_profile.service import create_audit_record
from src.modules.user.models import User

router = APIRouter()


@router.get("/")
async def get_product_cost_estimation_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> List[CostEstimationResponse]:
    cost_estimations = await get_product_cost_estimation(product.id)
    return cost_estimations


@router.post("/save")
async def save_product_cost_estimation_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    cost_estimation: SaveCostEstimationRequest,
) -> CostEstimationResponse:
    saved_estimation = await save_product_cost_estimation(product.id, cost_estimation)
    await create_audit_record(
        product,
        current_user,
        "Save product cost estimation",
        {
            "cost_estimation_id": saved_estimation.id,
            "payload": cost_estimation.model_dump(),
        },
    )
    return saved_estimation.to_cost_estimation_response(product.name, product.code)
