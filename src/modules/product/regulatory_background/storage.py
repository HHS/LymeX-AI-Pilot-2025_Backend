import asyncio
from typing import TypedDict
import mimetypes
from loguru import logger
from src.infrastructure.minio import (
    copy_objects,
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
    list_objects,
    remove_object,
)
from src.modules.product.regulatory_background.schema import (
    RegulatoryBackgroundDocumentResponse,
)
from src.modules.product.storage import get_product_folder
import base64
import fastavro
import io
from minio.datatypes import Object


class RegulatoryBackgroundDocumentInfo(TypedDict):
    file_name: str
    author: str


async def analyze_regulatory_background_document(
    obj: Object,
) -> RegulatoryBackgroundDocumentResponse:
    document_name = obj.object_name.split("/")[-1]
    regulatory_background_document_info = analyze_regulatory_background_document_info(
        document_name.split(".")[0]
    )
    file_name = regulatory_background_document_info["file_name"]
    document = RegulatoryBackgroundDocumentResponse(
        document_name=document_name,
        file_name=file_name,
        url=await generate_get_object_presigned_url(obj.object_name),
        uploaded_at=obj.last_modified.isoformat(),
        author=regulatory_background_document_info["author"],
        content_type=obj.content_type
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream",
        size=obj.size,
    )
    return document


async def get_regulatory_background_documents(
    product_id: str,
) -> list[RegulatoryBackgroundDocumentResponse]:
    folder = get_regulatory_background_folder(product_id)
    objects = await list_objects(folder)
    logger.info(f"Objects: {[o.object_name for o in objects]}")
    documents = [
        analyze_regulatory_background_document(obj)
        for obj in objects
        if obj.is_dir is False
    ]
    documents = await asyncio.gather(*documents)
    return documents


async def get_upload_regulatory_background_document_url(
    product_id: str,
    regulatory_background_document_info: RegulatoryBackgroundDocumentInfo,
) -> str:
    extension = regulatory_background_document_info["file_name"].split(".")[-1]
    document_name = encode_regulatory_background_document_info(
        regulatory_background_document_info
    )
    document_name = f"{document_name}.{extension}"
    folder = get_regulatory_background_folder(product_id)
    object_name = f"{folder}/{document_name}"
    url = await generate_put_object_presigned_url(object_name)
    return url


async def delete_regulatory_background_document(
    product_id: str,
    document_name: str,
) -> None:
    folder = get_regulatory_background_folder(product_id)
    object_name = f"{folder}/{document_name}"
    await remove_object(object_name)


# ================ FOLDERS ====================


def get_regulatory_background_folder(
    product_id: str,
) -> str:
    product_folder = get_product_folder(product_id)
    return f"{product_folder}/regulatory_background"


# ================ UTILS ====================

REGULATORY_BACKGROUND_DOCUMENT_INFO_SCHEMA = {
    "type": "record",
    "name": "Document",
    "fields": [
        {"name": "file_name", "type": "string"},
        {"name": "author", "type": "string"},
    ],
}


def encode_regulatory_background_document_info(
    regulatory_background_document_info: RegulatoryBackgroundDocumentInfo,
) -> str:
    # avro encode then urlsafe base64 encode with no padding
    buffer = io.BytesIO()
    fastavro.schemaless_writer(
        buffer,
        REGULATORY_BACKGROUND_DOCUMENT_INFO_SCHEMA,
        regulatory_background_document_info,
    )
    raw_bytes = buffer.getvalue()
    encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    document_name = encoded.rstrip("=")
    return document_name


def analyze_regulatory_background_document_info(
    regulatory_background_document_info: str,
) -> RegulatoryBackgroundDocumentInfo:
    # urlsafe base64 decode then avro decode
    padding_needed = (-len(regulatory_background_document_info)) % 4
    padded_str = regulatory_background_document_info + ("=" * padding_needed)
    raw_bytes = base64.urlsafe_b64decode(padded_str)
    buffer = io.BytesIO(raw_bytes)
    regulatory_background_document_info = fastavro.schemaless_reader(
        buffer,
        REGULATORY_BACKGROUND_DOCUMENT_INFO_SCHEMA,
    )
    return regulatory_background_document_info


async def clone_regulatory_background_documents(
    product_id: str,
    new_product_id: str,
) -> None:
    folder = get_regulatory_background_folder(product_id)
    new_folder = get_regulatory_background_folder(new_product_id)
    await copy_objects(folder, new_folder)
