from beanie import PydanticObjectId
from src.modules.product.custom_test_plan.model import CustomTestPlan
from src.modules.product.custom_test_plan.schema import (
    SaveCustomTestPlanRequest,
)
from typing import List
from datetime import datetime, timedelta

async def get_product_custom_test_plan(
    product_id: str | PydanticObjectId,
) -> List[CustomTestPlan]:
    test_plans = await CustomTestPlan.find({"product_id": str(product_id)}).to_list()
    if not test_plans:
        # Create dummy data
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=4)
        dummy_plan = CustomTestPlan(
            product_id=str(product_id),
            required_tests=[],
            internal_testing=True,
            external_testing=False,
            start_date=start_date,
            end_date=end_date,
            duration="4",
        )
        await dummy_plan.save()
        return [dummy_plan]
    return test_plans

async def save_product_custom_test_plan(
    product_id: str | PydanticObjectId, test_plan: SaveCustomTestPlanRequest
) -> CustomTestPlan:
    existing_plan = await CustomTestPlan.find_one({"product_id": str(product_id)})
    if existing_plan:
        # Update existing plan
        for field, value in test_plan.model_dump().items():
            setattr(existing_plan, field, value)
        existing_plan.updated_at = datetime.now()
        await existing_plan.save()
        return existing_plan
    
    # Create new plan if none exists
    new_plan = CustomTestPlan(
        product_id=str(product_id),
        **test_plan.model_dump(),
    )
    await new_plan.save()
    return new_plan
