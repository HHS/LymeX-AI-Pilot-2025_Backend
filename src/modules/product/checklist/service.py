from datetime import datetime, timezone
from typing import Any
from beanie import PydanticObjectId
from loguru import logger
from fastapi import HTTPException, UploadFile
import io
import uuid
import asyncio
from src.modules.product.models import Product
from src.modules.product.checklist.model import Checklist
from src.modules.product.product_profile.analyze_product_profile_progress import (
    AnalyzeProductProfileProgress,
)
from src.modules.product.product_profile.model import (
    ProductProfile,
    ProductProfileAudit,
)
from src.modules.product.product_profile.storage import clone_product_profile_documents
from src.modules.user.models import User
from src.infrastructure.minio import minio_client, generate_get_object_presigned_url
from src.environment import environment


async def get_analyze_product_profile_progress_or_default(
    product_id: str | PydanticObjectId,
) -> AnalyzeProductProfileProgress:
    """Get analyze progress or return a default one if not found"""
    analyze_product_profile_progress = await AnalyzeProductProfileProgress.find_one(
        AnalyzeProductProfileProgress.product_id == str(product_id),
    )
    if not analyze_product_profile_progress:
        # Return a default progress object
        analyze_product_profile_progress = AnalyzeProductProfileProgress(
            product_id=str(product_id),
            total_files=0,
            processed_files=0,
            updated_at=datetime.now(timezone.utc),
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
    logger.info(f"Creating audit record: {audit_record}")
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
    from src.modules.product.product_profile.storage import (
        get_product_profile_folder,
        analyze_profile_document_info,
    )

    # Get all files from the product profile folder
    folder = get_product_profile_folder(product_id)

    # List all objects in the product profile folder
    objects = await asyncio.to_thread(
        minio_client.list_objects,
        bucket_name=environment.minio_bucket,
        prefix=folder,
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
        document_name = obj.object_name.split("/")[-1]

        try:
            # Decode the Avro-encoded filename to get original filename and author
            encoded_name = document_name.split(".")[0]  # Remove file extension
            profile_document_info = analyze_profile_document_info(encoded_name)
            original_filename = profile_document_info["file_name"]
            author = profile_document_info["author"]
        except Exception as e:
            # Fallback for any decoding errors
            original_filename = document_name
            author = "Unknown"

        documents.append(
            {
                "document_name": original_filename,
                "file_name": original_filename,
                "url": url,
                "uploaded_at": (
                    obj.last_modified.isoformat() if obj.last_modified else ""
                ),
                "author": author,
                "size": obj.size,
            }
        )

    return documents


def get_checklist_folder(product_id: str, question_number: str) -> str:
    """Get the folder path for checklist files"""
    return f"product/{product_id}/checklist/{question_number}"


async def upload_checklist_file(
    product_id: str, question_number: str, file: UploadFile
) -> dict[str, Any]:
    """Upload a checklist file to MinIO storage for a specific question"""
    # Validate that the question exists in the checklist
    checklist = await Checklist.find_one({"product_id": product_id})
    if not checklist:
        raise HTTPException(
            status_code=404, detail="Checklist not found for this product"
        )

    # Check if the question exists in the checklist
    question_exists = any(
        q.question_number == question_number for q in checklist.answers
    )
    if not question_exists:
        raise HTTPException(status_code=404, detail="Question not found in checklist")

    # Generate a unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    object_name = (
        f"{get_checklist_folder(product_id, question_number)}/{unique_filename}"
    )
    file_content = await file.read()

    minio_client.put_object(
        bucket_name=environment.minio_bucket,
        object_name=object_name,
        length=len(file_content),
        data=io.BytesIO(file_content),
        content_type=file.content_type,
    )

    url = await generate_get_object_presigned_url(object_name)
    return {
        "object_name": object_name,
        "url": url,
        "question_number": question_number,
        "message": "File uploaded successfully for question",
    }


async def get_checklist_documents(
    product_id: str, question_number: str = None
) -> dict[str, Any]:
    """Get checklist documents for a product, optionally filtered by question_number"""
    if question_number:
        # Get documents for a specific question
        prefix = f"{get_checklist_folder(product_id, question_number)}/"
    else:
        # Get all documents for the product
        prefix = f"product/{product_id}/checklist/"

    objects = await asyncio.to_thread(
        minio_client.list_objects,
        bucket_name=environment.minio_bucket,
        prefix=prefix,
        recursive=True,
    )

    documents = []
    for obj in objects:
        url = await generate_get_object_presigned_url(obj.object_name)
        documents.append(
            {
                "object_name": obj.object_name,
                "url": url,
                "question_number": (
                    question_number
                    if question_number
                    else (
                        obj.object_name.split("/")[2]
                        if len(obj.object_name.split("/")) > 2
                        else None
                    )
                ),
            }
        )

    return {"documents": documents}
