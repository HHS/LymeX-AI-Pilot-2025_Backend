from typing import Annotated, List
from fastapi import APIRouter, Depends
from src.modules.product.models import Product
from src.modules.product.dependencies import get_current_product
from src.modules.product.custom_test_plan.service import (
    get_product_custom_test_plan,
    save_product_custom_test_plan,
)
from src.modules.product.custom_test_plan.schema import (
    CustomTestPlanResponse,
    SaveCustomTestPlanRequest,
)

router = APIRouter()

@router.get("/")
async def get_product_custom_test_plan_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> List[CustomTestPlanResponse]:
    test_plans = await get_product_custom_test_plan(product.id)
    return [tp.to_custom_test_plan_response() for tp in test_plans]

@router.post("/save")
async def save_product_custom_test_plan_handler(
    product: Annotated[Product, Depends(get_current_product)],
    test_plan: SaveCustomTestPlanRequest,
) -> CustomTestPlanResponse:
    saved_plan = await save_product_custom_test_plan(product.id, test_plan)
    return saved_plan.to_custom_test_plan_response()
