from beanie import PydanticObjectId
from src.modules.product.performance_testing.model import (
    AnalyzePerformanceTestingProgress,
    PerformanceTestPlan,
)


async def get_performance_test_plan(
    product_id: str | PydanticObjectId,
) -> PerformanceTestPlan | None:
    performance_testing = await PerformanceTestPlan.find_one(
        PerformanceTestPlan.product_id == str(product_id),
    )
    return performance_testing


async def get_analyze_performance_testing_progress(
    product_id: str,
) -> AnalyzePerformanceTestingProgress | None:
    analyze_performance_testing_progress = (
        await AnalyzePerformanceTestingProgress.find_one(
            AnalyzePerformanceTestingProgress.product_id == str(product_id),
        )
    )
    if not analyze_performance_testing_progress:
        return None
    return analyze_performance_testing_progress


async def clone_performance_testing(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    performance_test_plan = await get_performance_test_plan(
        product_id=product_id,
    )
    if performance_test_plan:
        new_performance_test_plan = PerformanceTestPlan(
            **performance_test_plan.model_dump(exclude={"id", "product_id"}),
            product_id=str(new_product_id),
        )
        await new_performance_test_plan.insert()
