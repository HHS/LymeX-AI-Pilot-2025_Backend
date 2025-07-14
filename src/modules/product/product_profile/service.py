from datetime import datetime, timezone
from typing import Any
from beanie import PydanticObjectId
from src.modules.product.models import Product
from src.modules.product.product_profile.analyze_product_profile_progress import AnalyzeProductProfileProgress
from src.modules.product.product_profile.model import (
    ProductProfile,
    ProductProfileAudit,
)
import asyncio
from src.modules.product.product_profile.storage import clone_product_profile_documents
from src.modules.product.storage import get_product_folder
from src.modules.user.models import User
from src.infrastructure.minio import minio_client, generate_get_object_presigned_url
from src.environment import environment


def get_profile_folder(
    company_id: str,
    product_id: str,
) -> str:
    product_folder = get_product_folder(company_id, product_id)
    return f"{product_folder}/profile"


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


async def get_product_documents(product_id: str) -> list[dict]:
    """Get all documents uploaded for a product"""
    # Get all files from the product files folder
    product_folder = get_product_folder(product_id)
    files_folder = f"{product_folder}/files/"

    # List all objects in the product files folder
    objects = await asyncio.to_thread(
        minio_client.list_objects,
        bucket_name=environment.minio_bucket,
        prefix=files_folder,
        recursive=True,
    )

    documents = []
    for obj in objects:
        # Skip directories
        if obj.is_dir:
            continue

        # Generate presigned URL for the document
        url = await generate_get_object_presigned_url(obj.object_name)

        # Extract filename from object name
        filename = obj.object_name.split("/")[-1]

        # Remove UUID prefix if present (from our upload logic)
        if "_" in filename:
            parts = filename.split("_", 1)
            if len(parts) == 2:
                original_filename = parts[1]
            else:
                original_filename = filename
        else:
            original_filename = filename

        documents.append(
            {
                "document_name": original_filename,
                "file_name": original_filename,
                "url": url,
                "uploaded_at": (
                    obj.last_modified.isoformat() if obj.last_modified else ""
                ),
                "author": "System",  # We don't track author in MinIO metadata
                "size": obj.size,
            }
        )

    return documents
