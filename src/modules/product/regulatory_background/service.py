from typing import Dict, Any
from fastapi import HTTPException, UploadFile
from beanie import PydanticObjectId
from datetime import datetime
import io
import asyncio
import uuid

from src.infrastructure.minio import minio_client, generate_get_object_presigned_url
from src.environment import environment
from src.modules.product.regulatory_background.model import RegulatoryBackground
from src.modules.product.regulatory_background.schema import (
    RegulatoryBackgroundResponse,
    RegulatorySummary,
    RegulatoryFinding,
    RegulatoryConflict,
    SummaryHighlight,
)
from src.modules.product.models import Product


def get_regulatory_background_folder(product_id: str) -> str:
    """Get the folder path for regulatory background files"""
    return f"product/{product_id}/regulatory_background"


async def get_product_info(product_id: str) -> tuple[str, str | None]:
    """Get product name and code for a given product ID"""
    product = await Product.get(product_id)
    product_name = product.name if product else ""
    product_code = product.code if product else None
    return product_name, product_code


async def upload_regulatory_background_file(
    product_id: str, file: UploadFile
) -> Dict[str, Any]:
    """Upload a regulatory background file to MinIO storage"""
    # Validate that the product exists
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate a unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    object_name = f"{get_regulatory_background_folder(product_id)}/{unique_filename}"
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
        "message": "Regulatory background file uploaded successfully",
    }


async def get_regulatory_background_documents(product_id: str) -> Dict[str, Any]:
    """Get regulatory background documents for a product"""
    # Validate that the product exists
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prefix = f"{get_regulatory_background_folder(product_id)}/"

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
                "filename": (
                    obj.object_name.split("/")[-1]
                    if "/" in obj.object_name
                    else obj.object_name
                ),
            }
        )

    return {"documents": documents}


def create_mock_regulatory_background(product_id: str) -> RegulatoryBackground:
    """Create a mock regulatory background entry with sample data"""

    # Create summary with highlights
    summary = RegulatorySummary(
        title="Regulatory Overview",
        description="This product has a prior regulatory engagement with the FDA, including a pre-submission meeting in May 2023. FDA feedback suggested a clinical trial may not be necessary, but requested additional data and clarification around intended use. No predicate device reference or risk classification was detected.",
        highlights=[
            SummaryHighlight(
                title="Previous FDA Communication",
                detail="Pre-submission meeting (May 2023)",
            ),
            SummaryHighlight(
                title="FDA Feedback Summary",
                detail="Clinical trial not required per FDA call; additional data requested",
            ),
        ],
    )

    # Create findings
    findings = [
        RegulatoryFinding(
            status="found",
            field="predicateDevice",
            label="Predicate Device Reference",
            value="Device similar to predicate K123456",
            source_file="pre_sub_feedback.pdf",
            source_page=4,
            tooltip=None,
            suggestion=None,
            confidence_score=None,
            user_action=None,
        ),
        RegulatoryFinding(
            status="found",
            field="clinicalTrialGuidance",
            label="Clinical Trial Requirements",
            value="Clinical trial not required per FDA call",
            source_file="investor_deck.pptx",
            source_page=6,
            tooltip=None,
            suggestion=None,
            confidence_score=92.0,
            user_action=True,
        ),
        RegulatoryFinding(
            status="missing",
            field="riskClassification",
            label="Risk Classification",
            value="No classification or exemption detected",
            source_file=None,
            source_page=None,
            tooltip="Terms like 'Class II', '510(k)', or 'exempt' were not found in uploaded documents.",
            suggestion="Specify the product's risk class or exemption status.",
            confidence_score=None,
            user_action=None,
        ),
        RegulatoryFinding(
            status="found",
            field="regulatoryHistory",
            label="Regulatory Submission History",
            value="Pre-submission held May 2023. FDA requested more data.",
            source_file="pre_sub_feedback.pdf",
            source_page=1,
            tooltip=None,
            suggestion=None,
            confidence_score=None,
            user_action=False,
        ),
        RegulatoryFinding(
            status="missing",
            field="intendedUse",
            label="Intended Use Statement",
            value="No intended use information detected.",
            source_file=None,
            source_page=None,
            tooltip="No terms like 'intended use', 'indication', or 'user population' found in uploaded documents.",
            suggestion="Add a paragraph clearly defining the intended use context.",
            confidence_score=None,
            user_action=None,
        ),
    ]

    # Create conflicts
    conflicts = [
        RegulatoryConflict(
            field="pediatricUse",
            phrase="Not intended for pediatric use",
            conflict="FDA flagged pediatric device review",
            source="pre_sub_feedback.pdf",
            suggestion="Review and align statements regarding pediatric population.",
            user_action=None,
        ),
        RegulatoryConflict(
            field="useEnvironment",
            phrase="Device is intended for home use",
            conflict="Submission lists hospital as primary setting",
            source="510k_summary.pdf",
            suggestion="Clarify intended use environment consistently across documents.",
            user_action=True,
        ),
        RegulatoryConflict(
            field="sterility",
            phrase="Sterile, single-use only",
            conflict="Labeling draft omits sterility statement",
            source="labeling_draft.docx",
            suggestion="Ensure sterility status is consistently documented across files.",
            user_action=None,
        ),
    ]

    # Create and return the mock regulatory background
    return RegulatoryBackground(
        product_id=product_id,
        summary=summary,
        findings=findings,
        conflicts=conflicts,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


async def get_regulatory_background(
    product_id: str | PydanticObjectId,
) -> RegulatoryBackgroundResponse:
    """Get regulatory background for a product with product information"""
    # Get product information
    product_name, product_code = await get_product_info(str(product_id))

    # Find the regulatory background
    regulatory_bg = await RegulatoryBackground.find_one({"product_id": str(product_id)})

    if not regulatory_bg:
        # Create mock entry with sample data
        regulatory_bg = create_mock_regulatory_background(str(product_id))
        # Save the mock entry to the database
        await regulatory_bg.insert()

    # Convert to response format with product data
    return regulatory_bg.to_regulatory_background_response(product_name, product_code)
