from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.product_profile.model import (
    AnalyzeProductProfileProgress,
    ProductProfile,
)
from src.modules.product.storage import get_product_folder


def get_profile_folder(
    company_id: str,
    product_id: str,
) -> str:
    product_folder = get_product_folder(company_id, product_id)
    return f"{product_folder}/profile"


async def get_analyze_product_profile_progress(
    product_id: str,
) -> AnalyzeProductProfileProgress:
    analyze_product_profile_progress = await AnalyzeProductProfileProgress.find_one(
        AnalyzeProductProfileProgress.product_id == product_id,
    )
    if not analyze_product_profile_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyze product profile progress not found",
        )
    return analyze_product_profile_progress


async def delete_product_profile(
    product_id: str,
) -> None:
    await AnalyzeProductProfileProgress.find(
        AnalyzeProductProfileProgress.product_id == product_id,
    ).delete_many()
    await ProductProfile.find(
        ProductProfile.product_id == product_id,
    ).delete_many()


async def get_product_profile(
    product_id: str | PydanticObjectId,
) -> ProductProfile | None:
    product_profile = await ProductProfile.find_one(
        ProductProfile.product_id == str(product_id),
    )
    return product_profile
