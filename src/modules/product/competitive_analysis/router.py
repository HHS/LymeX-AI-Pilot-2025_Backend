from typing import Annotated
from fastapi import APIRouter, Depends

from src.modules.product.competitive_analysis.model import (
    AnalyzeCompetitiveAnalysisProgress,
)
from src.modules.product.product_profile.service import get_product_profile
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from src.modules.product.competitive_analysis.storage import (
    delete_competitive_analysis_document,
    get_competitive_analysis_documents,
    get_upload_competitive_analysis_document_url,
)
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product
from src.celery.tasks.analyze_competitive_analysis import (
    analyze_competitive_analysis_task,
)
from src.modules.product.competitive_analysis.schema import (
    AnalyzeCompetitiveAnalysisProgressResponse,
    CompetitiveAnalysisDocumentResponse,
    CompetitiveAnalysisResponse,
    UpdateCompetitiveAnalysisRequest,
    UploadTextInputDocumentRequest,
)
from src.modules.product.competitive_analysis.service import (
    delete_competitive_analysis,
    get_all_product_competitive_analysis,
    get_analyze_competitive_analysis_progress,
    get_product_competitive_analysis,
    update_competitive_analysis,
)
import httpx


router = APIRouter()


@router.get("/analyze-progress")
async def get_analyze_competitive_analysis_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeCompetitiveAnalysisProgressResponse:
    analyze_competitive_analysis_progress = (
        await get_analyze_competitive_analysis_progress(
            str(product.id),
        )
    )
    return (
        analyze_competitive_analysis_progress.to_analyze_competitive_analysis_progress_response()
    )


@router.post("/analyze")
async def analyze_competitive_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await AnalyzeCompetitiveAnalysisProgress.find(
        AnalyzeCompetitiveAnalysisProgress.reference_product_id == str(product.id),
    ).delete_many()
    analyze_competitive_analysis_task.delay(str(product.id))


@router.get("/document")
async def get_competitive_analysis_document_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[CompetitiveAnalysisDocumentResponse]:
    competitive_analysis_documents = await get_competitive_analysis_documents(
        str(product.id),
    )
    return competitive_analysis_documents


@router.get("/document/upload-url")
async def get_upload_competitive_analysis_document_url_handler(
    file_name: str,
    category: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> str:
    upload_url = await get_upload_competitive_analysis_document_url(
        str(product.id),
        {
            "file_name": file_name,
            "author": current_user.email,
            "category": category,
        },
    )
    return upload_url


@router.put("/document/text-input")
async def upload_competitive_analysis_text_input_handler(
    payload: UploadTextInputDocumentRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    upload_url = await get_upload_competitive_analysis_document_url(
        str(product.id),
        {
            "file_name": "TextInput.txt",
            "author": current_user.email,
            "category": payload.category,
        },
    )
    async with httpx.AsyncClient() as client:
        await client.put(
            upload_url,
            data=payload.text,
            headers={"Content-Type": "text/plain"},
        )


@router.delete("/document/{document_name}")
async def delete_competitive_analysis_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_competitive_analysis_document(
        str(product.id),
        document_name,
    )


@router.get("/result")
async def get_all_competitive_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[CompetitiveAnalysisResponse]:
    competitive_analysis = await get_all_product_competitive_analysis(str(product.id))
    product_profile = await get_product_profile(product.id)
    this_product_competitive_analysis = CompetitiveAnalysisResponse(
        id=str(product.id),
        product_name=product.name,
        reference_number=product_profile.reference_number,
        regulatory_pathway=product_profile.regulatory_pathway,
        fda_approved=product_profile.fda_approved,
        is_ai_generated=False,
        confidence_score=product_profile.confidence_score,
        sources=product_profile.sources,
    )
    return [
        this_product_competitive_analysis,
        *[await i.to_competitive_analysis_response() for i in competitive_analysis],
    ]


@router.get("/result/{competitive_analysis_id}")
async def get_competitive_analysis_by_id_handler(
    competitive_analysis_id: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> CompetitiveAnalysisResponse:
    raise NotImplementedError("This endpoint is not implemented yet.")
    competitive_analysis = await get_product_competitive_analysis(
        str(product.id),
        competitive_analysis_id,
    )
    competitive_analysis_response = (
        await competitive_analysis.to_competitive_analysis_response()
    )
    return competitive_analysis_response


@router.delete("/result/{competitive_analysis_id}")
async def delete_competitive_analysis_handler(
    competitive_analysis_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_competitive_analysis(
        str(product.id),
        competitive_analysis_id,
    )


@router.patch("/result/{competitive_analysis_id}")
async def update_competitive_analysis_handler(
    competitive_analysis_id: str,
    payload: UpdateCompetitiveAnalysisRequest,
    product: Annotated[Product, Depends(get_current_product)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> CompetitiveAnalysisResponse:
    competitive_analysis = await update_competitive_analysis(
        str(product.id),
        competitive_analysis_id,
        payload,
    )
    competitive_analysis_response = (
        await competitive_analysis.to_competitive_analysis_response()
    )
    return competitive_analysis_response
