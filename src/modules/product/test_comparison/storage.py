import asyncio

from beanie import PydanticObjectId
from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
    list_objects,
)
from src.modules.product.storage import get_product_folder


def get_test_comparison_note_document_folder(
    product_id: str,
) -> str:
    product_folder = get_product_folder(product_id)
    return f"{product_folder}/test_comparison"


async def get_upload_test_comparison_note_document_url(
    product_id: str | PydanticObjectId,
    file_name: str,
) -> str:
    folder = get_test_comparison_note_document_folder(str(product_id))
    object_name = f"{folder}/{file_name}"
    url = await generate_put_object_presigned_url(object_name)
    return url


async def get_test_comparison_note_document_urls(
    product_id: str | PydanticObjectId,
) -> list[str]:
    folder = get_test_comparison_note_document_folder(str(product_id))
    objects = await list_objects(folder)
    document_urls = [
        generate_get_object_presigned_url(obj.object_name)
        for obj in objects
        if obj.is_dir is False
    ]
    document_urls = await asyncio.gather(*document_urls)
    return document_urls
