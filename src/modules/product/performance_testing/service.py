from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.performance_testing.model import (
    AnalyzePerformanceTestingProgress,
    PerformanceTesting,
)
from src.modules.product.performance_testing.schema import (
    CreatePerformanceTestingRequest,
    PerformanceTestingStatus,
)


async def get_performance_testing_by_name(
    product_id: str | PydanticObjectId,
    test_name: str,
) -> PerformanceTesting | None:
    performance_testing = await PerformanceTesting.find_one(
        PerformanceTesting.product_id == str(product_id),
        PerformanceTesting.test_name == test_name,
    )
    return performance_testing


async def create_performance_testing(
    product_id: str | PydanticObjectId,
    payload: CreatePerformanceTestingRequest,
) -> PerformanceTesting:
    existing_test = await get_performance_testing_by_name(
        product_id=product_id,
        test_name=payload.test_name,
    )
    if existing_test:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Performance testing with name '{payload.test_name}' already exists for product ID '{product_id}'.",
        )
    performance_testing = PerformanceTesting(
        product_id=str(product_id),
        test_name=payload.test_name,
        test_description=payload.test_description,
        status=payload.status or PerformanceTestingStatus.PENDING,
        risk_level=payload.risk_level,
    )
    await performance_testing.save()
    return performance_testing


async def get_performance_testing(
    performance_testing_id: str | PydanticObjectId,
) -> PerformanceTesting | None:
    performance_testing = await PerformanceTesting.get(performance_testing_id)
    return performance_testing


async def get_product_performance_testings(
    product_id: str | PydanticObjectId,
) -> list[PerformanceTesting]:
    performance_testings = await PerformanceTesting.find(
        PerformanceTesting.product_id == str(product_id)
    ).to_list()
    return performance_testings


async def clone_performance_testing(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_testings = await PerformanceTesting.find(
        PerformanceTesting.product_id == str(product_id),
    ).to_list()
    if existing_testings:
        await PerformanceTesting.insert_many(
            [
                PerformanceTesting(
                    **testing.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for testing in existing_testings
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
