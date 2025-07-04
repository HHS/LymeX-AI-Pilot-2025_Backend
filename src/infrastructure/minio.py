import asyncio
from datetime import timedelta
from fastapi import FastAPI
from minio import Minio
from minio.commonconfig import CopySource
from minio.datatypes import Object
from src.environment import environment
from loguru import logger

app = FastAPI()

minio_client = Minio(
    environment.minio_internal_endpoint.removeprefix("http://").removeprefix(
        "https://"
    ),
    access_key=environment.minio_root_user,
    secret_key=environment.minio_root_password,
    secure=environment.minio_internal_endpoint.startswith("https://"),
)


async def generate_put_object_presigned_url(
    object_name: str,
    expiration_seconds=300,
) -> str:
    put_object_presigned_url = await asyncio.to_thread(
        minio_client.presigned_put_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
        expires=timedelta(seconds=expiration_seconds),
    )
    return put_object_presigned_url


async def generate_get_object_presigned_url(
    object_name: str,
    expiration_seconds=300,
) -> str:
    get_object_presigned_url = await asyncio.to_thread(
        minio_client.presigned_get_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
        expires=timedelta(seconds=expiration_seconds),
    )
    return get_object_presigned_url


async def list_objects(prefix: str, recursive=False) -> list[Object]:
    if not prefix.endswith("/"):
        prefix += "/"
    objects = await asyncio.to_thread(
        minio_client.list_objects,
        bucket_name=environment.minio_bucket,
        prefix=prefix,
        recursive=recursive,
    )
    return list(objects)


async def remove_object(object_name: str) -> None:
    await asyncio.to_thread(
        minio_client.remove_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
    )


async def get_object(object_name: str) -> bytes:
    data = await asyncio.to_thread(
        minio_client.get_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
    )
    return data.read()


async def list_objects_(prefix: str):
    """Helper to list all objects under a prefix asynchronously."""

    # MinIO SDK is blocking, so wrap in a thread
    def _list():
        return list(
            minio_client.list_objects(
                environment.minio_bucket, prefix=prefix, recursive=True
            )
        )

    return await asyncio.to_thread(_list)


async def copy_objects(source_prefix: str, destination_prefix: str) -> None:
    if not source_prefix.endswith("/"):
        source_prefix += "/"
    if not destination_prefix.endswith("/"):
        destination_prefix += "/"

    logger.info(f"Listing objects in bucket '{environment.minio_bucket}' with prefix '{source_prefix}'")
    def _list():
        return list(
            minio_client.list_objects(
                environment.minio_bucket, prefix=source_prefix, recursive=True
            )
        )

    objects = await asyncio.to_thread(_list)
    logger.info(f"Found {len(objects)} objects to copy from '{source_prefix}' to '{destination_prefix}'")

    tasks = []
    for obj in objects:
        source_object_name = obj.object_name
        destination_object_name = (
            destination_prefix + source_object_name[len(source_prefix):]
        )
        logger.debug(f"Copying '{source_object_name}' to '{destination_object_name}'")
        copy_source = CopySource(environment.minio_bucket, source_object_name)
        task = asyncio.to_thread(
            minio_client.copy_object,
            environment.minio_bucket,
            destination_object_name,
            copy_source,
        )
        tasks.append(task)

    if tasks:
        logger.info(f"Starting copy of {len(tasks)} objects...")
        await asyncio.gather(*tasks)
        logger.info("Copy operation completed.")
    else:
        logger.info("No objects to copy.")
