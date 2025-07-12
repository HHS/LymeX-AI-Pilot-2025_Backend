from datetime import datetime, timezone

from fastapi import HTTPException, status

from src.celery.tasks.analyze_claim_builder import analyze_claim_builder_task
from src.celery.tasks.analyze_clinical_trial import analyze_clinical_trial_task
from src.celery.tasks.analyze_competitive_analysis import (
    analyze_competitive_analysis_task,
)
from src.celery.tasks.analyze_milestone_planning import analyze_milestone_planning_task
from src.celery.tasks.analyze_product_profile import analyze_product_profile_task
from src.celery.tasks.analyze_regulatory_pathway import analyze_regulatory_pathway_task
from src.celery.tasks.analyze_test_comparison import analyze_test_comparison_task
import io
import uuid
from fastapi import UploadFile
from src.infrastructure.minio import list_objects, remove_object, minio_client
from src.environment import environment
from src.modules.company.models import Company
from src.modules.product.models import Product
from src.modules.product.schema import CreateProductRequest
from src.modules.product.storage import get_product_folder
from src.modules.user.models import User


async def get_products(
    current_company: Company,
) -> list[Product]:
    products = await Product.find(
        Product.company_id == str(current_company.id),
    ).to_list()
    return products


async def create_product(
    payload: CreateProductRequest,
    current_user: User,
    current_company: Company,
) -> Product:
    # Check if product name already exists for this company
    product_name_exists = await Product.find_one(
        Product.company_id == str(current_company.id),
        Product.name == payload.name,
    )
    if product_name_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name already exists for this company.",
        )

    # Check if product code already exists for this company (if model is provided)
    if payload.model:
        product_code_exists = await Product.find_one(
            Product.company_id == str(current_company.id),
            Product.name == payload.name,
            Product.model == payload.model,
        )
        if product_code_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists for this company.",
            )
    now = datetime.now(timezone.utc)
    product = Product(
        code=payload.code,
        name=payload.name,
        model=payload.model or "Default Model",
        revision=payload.revision or "1.0",
        intend_use=payload.intend_use or "General Use",
        patient_contact=(
            payload.patient_contact if payload.patient_contact is not None else False
        ),
        category=payload.category or "General",
        company_id=str(current_company.id),
        created_by=str(current_user.id),
        created_at=now,
        updated_by=str(current_user.id),
        updated_at=now,
    )
    await product.insert()
    return product


async def delete_product_folder(
    product_id: str,
) -> None:
    folder = get_product_folder(product_id)
    objects = await list_objects(folder, True)
    for obj in objects:
        if obj.is_dir:
            continue
        await remove_object(obj.object_name)


async def analyze_all(
    product_id: str,
) -> None:
    analyze_claim_builder_task.delay(product_id)
    analyze_clinical_trial_task.delay(product_id)
    analyze_competitive_analysis_task.delay(product_id)
    analyze_milestone_planning_task.delay(product_id)
    analyze_product_profile_task.delay(product_id)
    analyze_regulatory_pathway_task.delay(product_id)
    analyze_test_comparison_task.delay(product_id)


async def upload_product_files(product_id: str, files: list[UploadFile]) -> list[dict]:
    """Upload files for a product to MinIO storage"""
    uploaded_files = []

    for file in files:
        # Generate a unique filename to prevent overwriting
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        object_name = f"{get_product_folder(product_id)}/files/{unique_filename}"
        file_content = await file.read()

        minio_client.put_object(
            bucket_name=environment.minio_bucket,
            object_name=object_name,
            length=len(file_content),
            data=io.BytesIO(file_content),
            content_type=file.content_type,
        )

        uploaded_files.append(
            {
                "original_filename": file.filename,
                "object_name": object_name,
                "content_type": file.content_type,
                "size": len(file_content),
            }
        )

    return uploaded_files
