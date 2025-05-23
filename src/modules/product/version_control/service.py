from datetime import datetime, timezone
from fastapi import HTTPException, status
import pymongo
from src.modules.product.claim_builder.model import ClaimBuilder, ClaimBuilderPydantic
from src.modules.product.version_control.model import ProductVersionControl


async def get_product_version_control(
    product_id: str,
) -> list[ProductVersionControl]:
    version_controls = (
        await ProductVersionControl.find(
            ProductVersionControl.product_id == product_id,
        )
        .sort(
            [
                (ProductVersionControl.major_version, pymongo.DESCENDING),
                (ProductVersionControl.minor_version, pymongo.DESCENDING),
            ]
        )
        .to_list()
    )
    return version_controls


async def promote_major_version(
    product_id: str,
    created_by: str,
) -> ProductVersionControl:
    last_version_controls = (
        await ProductVersionControl.find(
            ProductVersionControl.product_id == product_id,
        )
        .sort(
            [
                (ProductVersionControl.major_version, pymongo.DESCENDING),
                (ProductVersionControl.minor_version, pymongo.DESCENDING),
            ]
        )
        .limit(1)
        .first_or_none()
    )
    if not last_version_controls:
        raise HTTPException(
            status_code=status,
            detail="Product version control not found",
        )
    major_version = last_version_controls.major_version + 1
    minor_version = 0
    product_version_control = ProductVersionControl(
        product_id=product_id,
        major_version=major_version,
        minor_version=minor_version,
        comment="Promote major version",
        data=last_version_controls.data,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
    )
    await product_version_control.save()
    return product_version_control


async def get_latest_product_version_control(
    product_id: str,
) -> ProductVersionControl | None:
    version_control = (
        await ProductVersionControl.find(
            ProductVersionControl.product_id == product_id,
        )
        .sort(
            [
                (ProductVersionControl.major_version, pymongo.DESCENDING),
                (ProductVersionControl.minor_version, pymongo.DESCENDING),
            ]
        )
        .limit(1)
        .first_or_none()
    )
    return version_control


async def snapshot_minor_version(
    claim_builder: ClaimBuilder,
    comment: str,
    created_by: str,
) -> ProductVersionControl:
    last_version_controls = await get_latest_product_version_control(
        claim_builder.product_id
    )
    if last_version_controls:
        major_version = last_version_controls.major_version
        minor_version = last_version_controls.minor_version + 1
    else:
        major_version = 0
        minor_version = 1
    product_version_control = ProductVersionControl(
        product_id=claim_builder.product_id,
        major_version=major_version,
        minor_version=minor_version,
        comment=comment,
        data=claim_builder.to_claim_builder_pydantic(),
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
    )
    await product_version_control.save()
    return product_version_control


async def get_version_data(
    product_id: str,
    major_version: str,
    minor_version: str,
) -> ClaimBuilderPydantic:
    version_control = await ProductVersionControl.find_one(
        ProductVersionControl.product_id == product_id,
        ProductVersionControl.major_version == int(major_version),
        ProductVersionControl.minor_version == int(minor_version),
    )
    if not version_control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product version control not found",
        )
    if not version_control.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Malformed product version control data",
        )
    return version_control.data
