from beanie import PydanticObjectId
from src.modules.product.performance_testing.model import (
    AnalyzePerformanceTestingProgress,
    PerformanceTesting,
)


async def get_product_performance_testings(
    product_id: str | PydanticObjectId,
) -> list[PerformanceTesting]:
    product_performance_testings = await PerformanceTesting.find(
        PerformanceTesting.product_id == str(product_id)
    ).to_list()
    return product_performance_testings


async def clone_performance_testing(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_performance_testings = await PerformanceTesting.find(
        PerformanceTesting.product_id == str(product_id),
    ).to_list()
    if existing_performance_testings:
        await PerformanceTesting.insert_many(
            [
                PerformanceTesting(
                    **testing.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for testing in existing_performance_testings
            ]
        )


async def get_analyze_performance_testing_progress(
    product_id: str,
) -> AnalyzePerformanceTestingProgress | None:
    analyze_performance_testing_progress = (
        await AnalyzePerformanceTestingProgress.find_one(
            AnalyzePerformanceTestingProgress.product_id == product_id,
        )
    )
    if not analyze_performance_testing_progress:
        return None
    return analyze_performance_testing_progress
