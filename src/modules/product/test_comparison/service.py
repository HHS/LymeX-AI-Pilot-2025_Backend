from beanie import PydanticObjectId
from fastapi import HTTPException, status

from src.modules.product.test_comparison.model import (
    TestComparison,
)


async def get_product_all_test_comparison(
    product_id: str | PydanticObjectId,
) -> list[TestComparison]:
    product_test_comparisons = await TestComparison.find(
        TestComparison.product_id == str(product_id)
    ).to_list()
    return product_test_comparisons


async def get_product_test_comparison(
    comparison_id: str | PydanticObjectId,
    product_id: str | PydanticObjectId,
) -> TestComparison | None:
    product_test_comparison = await TestComparison.get(comparison_id)
    if not product_test_comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test comparison data not found for the product. Please analyze the product first.",
        )
    if product_test_comparison.product_id != str(product_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this test comparison.",
        )
    return product_test_comparison


async def clone_test_comparison(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_test_comparisons = await TestComparison.find(
        TestComparison.product_id == str(product_id),
    ).to_list()
    if existing_test_comparisons:
        await TestComparison.insert_many(
            [
                TestComparison(
                    **comparison.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for comparison in existing_test_comparisons
            ]
        )
