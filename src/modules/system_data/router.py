from typing import Annotated

from fastapi import APIRouter, Depends

from src.celery.tasks.index_system_data import index_system_data_task
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
from src.modules.system_data.storage import get_system_data_folder

router = APIRouter()


@router.get("/")
async def get_system_data_handler(
    _: Annotated[bool, Depends(require_system_admin)],
) -> list[GetDocumentResponse]:
    system_data_folder = get_system_data_folder()
    system_data = await list_objects(prefix=f"{system_data_folder}/")
    system_data = [document for document in system_data if not document.is_dir]
    file_names = [document.object_name.split("/")[-1] for document in system_data]
    file_urls = [
        await generate_get_object_presigned_url(
            object_name=document.object_name,
        )
        for document in system_data
    ]
    return [
        GetDocumentResponse(
            name=file_name,
            url=file_url,
        )
        for file_name, file_url in zip(file_names, file_urls)
    ]


@router.get("/upload-url")
async def get_upload_system_data_url_handler(
    file_name: str,
    _: Annotated[bool, Depends(require_system_admin)],
) -> UploadDocumentUrlResponse:
    system_data_folder = get_system_data_folder()
    object_name = f"{system_data_folder}/{file_name}"
    upload_system_data_url = await generate_put_object_presigned_url(
        object_name=object_name,
    )
    return {
        "url": upload_system_data_url,
    }


@router.delete("/delete-file")
async def delete_file_handler(
    file_name: str,
    _: Annotated[bool, Depends(require_system_admin)],
) -> None:
    system_data_folder = get_system_data_folder()
    object_name = f"{system_data_folder}/{file_name}"
    await remove_object(object_name=object_name)


@router.post("/index")
async def index_system_data_handler(
    _: Annotated[bool, Depends(require_system_admin)],
) -> None:
    index_system_data_task.delay()
