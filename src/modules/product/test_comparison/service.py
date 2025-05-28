from beanie import PydanticObjectId

from src.modules.product.test_comparison.model import (
    TestComparison,
    TestComparisonNote,
)


async def get_product_test_comparison(
    product_id: str | PydanticObjectId,
) -> TestComparison | None:
    product_test_comparison = await TestComparison.find_one(
        TestComparison.product_id == str(product_id)
    )
    return product_test_comparison


async def get_product_test_comparison_note(
    product_id: str | PydanticObjectId,
) -> TestComparisonNote | None:
    product_test_comparison = await TestComparisonNote.find_one(
        TestComparisonNote.product_id == str(product_id)
    )
    return product_test_comparison
