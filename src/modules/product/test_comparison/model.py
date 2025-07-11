from beanie import Document, PydanticObjectId
from src.modules.product.test_comparison.schema import (
    IdentifiedGapAndSuggestedAdjustment,
    TestComparisonResponse,
    TestInfo,
)
from src.modules.product.models import Product


class TestComparison(Document):
    product_id: str
    comparison_name: str
    requirements: list[TestInfo]
    comparator: list[TestInfo]
    identified_gaps_and_suggested_adjustments: list[IdentifiedGapAndSuggestedAdjustment]

    class Settings:
        name = "test_comparison"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_test_comparison_response(self) -> TestComparisonResponse:
        # Fetch product name
        product = await Product.get(self.product_id)
        product_name = product.name if product else "Unknown Product"

        return TestComparisonResponse(
            id=str(self.id),
            comparison_name=self.comparison_name,
            product_id=self.product_id,
            product_name=product_name,
            requirements=self.requirements,
            comparator=self.comparator,
            identified_gaps_and_suggested_adjustments=self.identified_gaps_and_suggested_adjustments,
        )
