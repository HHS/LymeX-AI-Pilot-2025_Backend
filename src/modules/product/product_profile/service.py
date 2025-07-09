from datetime import datetime, timezone
from typing import Any
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from src.modules.product.models import Product
from src.modules.product.product_profile.model import (
    AnalyzeProductProfileProgress,
    ProductProfile,
    ProductProfileAudit,
)
from src.modules.product.product_profile.storage import clone_product_profile_documents
from src.modules.product.storage import get_product_folder
from src.modules.user.models import User


def get_profile_folder(
    company_id: str,
    product_id: str,
) -> str:
    product_folder = get_product_folder(company_id, product_id)
    return f"{product_folder}/profile"


async def get_analyze_product_profile_progress(
    product_id: str | PydanticObjectId,
) -> AnalyzeProductProfileProgress:
    analyze_product_profile_progress = await AnalyzeProductProfileProgress.find_one(
        AnalyzeProductProfileProgress.product_id == str(product_id),
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


async def create_audit_record(
    product: Product,
    user: User,
    action: str,
    data: Any,
) -> ProductProfileAudit:
    audit_record = ProductProfileAudit(
        product_id=str(product.id),
        product_name=product.name,
        user_id=str(user.id),
        user_email=user.email,
        user_name=f"{user.first_name} {user.last_name}",
        action=action,
        data=data,
        timestamp=datetime.now(timezone.utc),
    )
    await audit_record.insert()
    return audit_record


async def clone_product_profile(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_profile = await ProductProfile.find(
        ProductProfile.product_id == str(product_id),
    ).to_list()

    if existing_profile:
        await ProductProfile.insert_many(
            [
                ProductProfile(
                    **profile.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for profile in existing_profile
            ]
        )

    analyze_progress = await AnalyzeProductProfileProgress.find_one(
        AnalyzeProductProfileProgress.product_id == str(product_id),
    )

    if analyze_progress:
        new_analyze_progress = AnalyzeProductProfileProgress(
            **analyze_progress.model_dump(exclude={"id", "product_id"}),
            product_id=str(new_product_id),
        )
        await new_analyze_progress.insert()

    await clone_product_profile_documents(
        product_id=str(product_id),
        new_product_id=str(new_product_id),
    )
