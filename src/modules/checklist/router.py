from typing import Annotated
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from src.modules.checklist.service import (
    create_master_checklist_from_json,
    get_master_checklist,
    upload_checklist_file,
    get_checklist_documents,
    get_or_create_checklist,
    submit_checklist_for_analysis,
)

from src.modules.product.dependencies import get_current_product
from src.modules.product.models import Product


router = APIRouter()


@router.post("/master-checklist")
async def create_master_checklist():
    """Create master checklist records from the existing JSON file"""
    try:
        return await create_master_checklist_from_json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating master checklist: {str(e)}"
        )


@router.get("/master-checklist")
async def get_master_checklist_endpoint():
    """Get all master checklist questions"""
    try:
        return await get_master_checklist()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching master checklist: {str(e)}"
        )


@router.post("/upload-file")
async def upload_checklist_image(
    product: Annotated[Product, Depends(get_current_product)],
    question_id: str = Query(..., description="Question ID to upload file for"),
    file: UploadFile = File(...),
):
    """Upload a checklist file for a specific question"""
    try:
        return await upload_checklist_file(str(product.id), question_id, file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_checklist_documents_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
    question_id: str = Query(
        None, description="Optional question ID to filter documents"
    ),
):
    """Get all checklist documents for a product, optionally filtered by question"""
    try:
        return await get_checklist_documents(str(product.id), question_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_or_create_checklist_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
):
    """Get checklist by product_id, create if not exists using master checklist"""
    try:
        return await get_or_create_checklist(str(product.id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting/creating checklist: {str(e)}"
        )


@router.post("/submit")
async def submit_checklist_endpoint(
    product: Annotated[Product, Depends(get_current_product)],
):
    """Submit checklist for AI analysis"""
    try:
        return await submit_checklist_for_analysis(str(product.id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error submitting checklist: {str(e)}"
        )
