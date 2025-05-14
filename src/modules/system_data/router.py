from typing import Annotated
from fastapi import APIRouter, Depends

from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
    list_objects,
    remove_object,
)
from src.modules.authorization.dependencies import require_system_admin
from src.modules.system_data.schema import (
    GetDocumentResponse,
    UploadDocumentUrlResponse,
)
from src.modules.system_data.storage import get_system_data_competitive_analysis_folder


router = APIRouter()


@router.get("/competitive-analysis")
async def get_competitive_analysis_handler(
    category: str,
    _: Annotated[bool, Depends(require_system_admin)],
) -> list[GetDocumentResponse]:
    competitive_analysis_folder = get_system_data_competitive_analysis_folder(category)
    competitive_analysis = await list_objects(prefix=f"{competitive_analysis_folder}/")
    competitive_analysis = [
        document for document in competitive_analysis if not document.is_dir
    ]
    file_names = [
        document.object_name.split("/")[-1] for document in competitive_analysis
    ]
    file_urls = [
        await generate_get_object_presigned_url(
            object_name=document.object_name,
        )
        for document in competitive_analysis
    ]
    return [
        GetDocumentResponse(
            name=file_name,
            url=file_url,
        )
        for file_name, file_url in zip(file_names, file_urls)
    ]


@router.get("/competitive-analysis/upload-url")
async def get_upload_competitive_analysis_url_handler(
    file_name: str,
    category: str,
    _: Annotated[bool, Depends(require_system_admin)],
) -> UploadDocumentUrlResponse:
    competitive_analysis_folder = get_system_data_competitive_analysis_folder(category)
    object_name = f"{competitive_analysis_folder}/{file_name}"
    upload_competitive_analysis_url = await generate_put_object_presigned_url(
        object_name=object_name,
    )
    return {
        "url": upload_competitive_analysis_url,
    }


@router.delete("/competitive-analysis/delete-file")
async def delete_file_handler(
    file_name: str,
    competitive_analysis_type: str,
    _: Annotated[bool, Depends(require_system_admin)],
) -> None:
    competitive_analysis_folder = get_system_data_competitive_analysis_folder(
        competitive_analysis_type
    )
    object_name = f"{competitive_analysis_folder}/{file_name}"
    await remove_object(object_name=object_name)
