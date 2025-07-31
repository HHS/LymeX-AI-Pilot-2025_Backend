import asyncio
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.product.competitive_analysis.analyze_competitive_analysis_progress import (
    AnalyzeCompetitiveAnalysisProgress,
    get_analyze_competitive_analysis_progress,
)
from src.modules.product.competitive_analysis.model import (
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
)
from src.modules.product.analyzing_status import (
    AnalyzingStatus,
    AnalyzingStatusResponse,
)
from src.modules.product.product_profile.service import (
    create_audit_record,
    get_product_profile,
)
from src.modules.authentication.dependencies import get_current_user
from src.modules.user.models import User
from src.modules.product.competitive_analysis.storage import (
    AnalysisDocumentInfo,
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
    AcceptCompetitiveAnalysisRequest,
    AnalyzeCompetitiveAnalysisProgressResponse,
    CompetitiveAnalysisCompareResponse,
    CompetitiveAnalysisDocumentResponse,
    CompetitiveAnalysisResponse,
    CompetitiveDeviceAnalysisResponse,
    UploadTextInputDocumentRequest,
)
from src.modules.product.competitive_analysis.service import (
    delete_competitive_analysis,
    get_all_product_competitive_analysis,
    get_product_competitive_analysis,
)
import httpx

from src.utils.string_to_id import string_to_id


router = APIRouter()


@router.get("/analyze-progress")
async def get_analyze_competitive_analysis_progress_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> AnalyzeCompetitiveAnalysisProgressResponse | AnalyzingStatusResponse:
    analyze_competitive_analysis_progress = (
        await get_analyze_competitive_analysis_progress(
            str(product.id),
        )
    )
    if not analyze_competitive_analysis_progress:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    return analyze_competitive_analysis_progress.to_analyze_competitive_analysis_progress_response()


@router.post("/analyze")
async def analyze_competitive_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
    user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    await AnalyzeCompetitiveAnalysisProgress.find(
        AnalyzeCompetitiveAnalysisProgress.product_id == str(product.id),
    ).delete_many()
    analyze_competitive_analysis_progress = AnalyzeCompetitiveAnalysisProgress(
        product_id=str(product.id),
        total_files=0,
        processed_files=0,
        updated_at=datetime.now(timezone.utc),
    )
    await analyze_competitive_analysis_progress.save()
    analyze_competitive_analysis_task.delay(str(product.id))
    await create_audit_record(
        product,
        user,
        "Analyze competitive analysis",
        {},
    )


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
    competitor_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> str:
    upload_url = await get_upload_competitive_analysis_document_url(
        str(product.id),
        AnalysisDocumentInfo(
            file_name=file_name,
            author=current_user.email,
            competitor_name=competitor_name,
        ),
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
        AnalysisDocumentInfo(
            file_name="TextInput.txt",
            author=current_user.email,
            competitor_name=payload.competitor_name,
        ),
    )
    async with httpx.AsyncClient() as client:
        await client.put(
            upload_url,
            data=payload.text,
            headers={"Content-Type": "text/plain"},
        )
    await create_audit_record(
        product,
        current_user,
        "Upload competitive analysis text input",
        payload.model_dump(),
    )


@router.delete("/document/{document_name}")
async def delete_competitive_analysis_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_competitive_analysis_document(
        str(product.id),
        document_name,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete competitive analysis document",
        {"document_name": document_name},
    )


@router.get("/result")
async def get_all_competitive_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[CompetitiveAnalysisResponse] | AnalyzingStatusResponse:
    competitive_analysis = await get_all_product_competitive_analysis(str(product.id))
    product_profile = await get_product_profile(product.id)
    if not product_profile:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )
    competitive_analysis_tasks = [
        i.to_competitive_analysis_response(product=product)
        for i in competitive_analysis
    ]
    competitive_analysis_responses = await asyncio.gather(*competitive_analysis_tasks)
    return competitive_analysis_responses


@router.get("/result/{competitive_analysis_id}/compare")
async def competitive_analysis_compare_handler(
    competitive_analysis_id: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> CompetitiveAnalysisCompareResponse | AnalyzingStatusResponse:
    competitive_analysis = await get_product_competitive_analysis(
        str(product.id),
        competitive_analysis_id,
    )
    competitive_analysis_response = (
        await competitive_analysis.to_competitive_analysis_response(product=product)
    )
    return competitive_analysis_response.comparison


@router.get("/compare-device-analysis-result")
async def get_competitive_analysis_compare_device_analysis_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[CompetitiveDeviceAnalysisResponse] | AnalyzingStatusResponse:
    competitive_analysis_compare_device_analysis = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == str(product.id),
    ).to_list()
    competitive_device_analysis_response_task = [
        i.to_competitive_device_analysis_response()
        for i in competitive_analysis_compare_device_analysis
    ]
    competitive_device_analysis_responses = await asyncio.gather(
        *competitive_device_analysis_response_task
    )
    return competitive_device_analysis_responses


@router.get("/result/{competitive_analysis_id}/compare-device-analysis")
async def competitive_analysis_compare_device_analysis_handler(
    competitive_analysis_id: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> CompetitiveDeviceAnalysisResponse | AnalyzingStatusResponse:
    competitive_analysis_id = string_to_id(competitive_analysis_id)
    competitive_analysis = await get_product_competitive_analysis(
        str(product.id),
        competitive_analysis_id,
    )
    return await competitive_analysis.to_competitive_device_analysis_response()


@router.delete("/result/{competitive_analysis_id}")
async def delete_competitive_analysis_handler(
    competitive_analysis_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_competitive_analysis(
        str(product.id),
        competitive_analysis_id,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete competitive analysis",
        {"competitive_analysis_id": competitive_analysis_id},
    )


# @router.patch("/result/{competitive_analysis_id}")
# async def update_competitive_analysis_handler(
#     competitive_analysis_id: str,
#     payload: UpdateCompetitiveAnalysisRequest,
#     product: Annotated[Product, Depends(get_current_product)],
#     current_user: Annotated[User, Depends(get_current_user)],
#     _: Annotated[bool, Depends(check_product_edit_allowed)],
# ) -> CompetitiveAnalysisResponse | AnalyzingStatusResponse:
#     competitive_analysis = await update_competitive_analysis(
#         str(product.id),
#         competitive_analysis_id,
#         payload,
#     )
#     product_profile = await get_product_profile(product.id)
#     if not product_profile:
#         return AnalyzingStatusResponse(
#             analyzing_status=AnalyzingStatus.IN_PROGRESS,
#         )
#     competitive_analysis_response = (
#         competitive_analysis.to_competitive_analysis_response(
#             product,
#             product_profile,
#         )
#     )
#     await create_audit_record(
#         product,
#         current_user,
#         "Update competitive analysis",
#         {
#             "competitive_analysis_id": competitive_analysis_id,
#             "payload": payload.model_dump(),
#         },
#     )
#     return competitive_analysis_response


@router.post("/accept/{competitive_analysis_id}")
async def accept_competitive_analysis_handler(
    payload: AcceptCompetitiveAnalysisRequest,
    competitive_analysis_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> CompetitiveAnalysisResponse | AnalyzingStatusResponse:
    competitive_analysis = await CompetitiveAnalysis.find_one(
        CompetitiveAnalysis.id == string_to_id(competitive_analysis_id),
        CompetitiveAnalysis.product_id == str(product.id),
    )
    if not competitive_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitive analysis not found",
        )
    competitive_analysis_detail = await CompetitiveAnalysisDetail.get(
        competitive_analysis.competitive_analysis_detail_id
    )
    competitive_analysis_detail.accepted = payload.accepted
    competitive_analysis_detail.accept_reject_reason = payload.accept_reject_reason
    competitive_analysis_detail.accept_reject_by = (
        f"{current_user.first_name} {current_user.last_name}"
    )
    await competitive_analysis_detail.save()

    await create_audit_record(
        product,
        current_user,
        "Accept competitive analysis",
        {
            "competitive_analysis_id": competitive_analysis_id,
            "payload": payload.model_dump(),
        },
    )
    product_profile = await get_product_profile(product.id)
    if not product_profile:
        return AnalyzingStatusResponse(
            analyzing_status=AnalyzingStatus.IN_PROGRESS,
        )

    return await competitive_analysis.to_competitive_analysis_response(product=product)
