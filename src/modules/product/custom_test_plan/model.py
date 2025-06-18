from beanie import Document
from typing import List
from datetime import datetime
from src.modules.product.custom_test_plan.schema import CustomTestPlanResponse

class CustomTestPlan(Document):
    product_id: str
    required_tests: List[str]
    internal_testing: bool
    external_testing: bool
    start_date: datetime
    end_date: datetime
    duration: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "custom_test_plan"

    def to_custom_test_plan_response(self) -> CustomTestPlanResponse:
        return CustomTestPlanResponse(
            id=str(self.id),
            product_id=self.product_id,
            required_tests=self.required_tests,
            internal_testing=self.internal_testing,
            external_testing=self.external_testing,
            start_date=self.start_date,
            end_date=self.end_date,
            duration=self.duration,
        )