import asyncio
from datetime import timedelta
from fastapi import FastAPI
from minio import Minio
from src.environment import environment

app = FastAPI()

minio_client = Minio(
    environment.minio_internal_endpoint.removeprefix("http://").removeprefix("https://"),
    access_key=environment.minio_root_user,
    secret_key=environment.minio_root_password,
    secure=environment.minio_internal_endpoint.startswith("https://"),
)


async def generate_put_object_presigned_url(
    object_name: str,
    expiration_seconds=300,
) -> str:
    return await asyncio.to_thread(
        minio_client.presigned_put_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
        expires=timedelta(seconds=expiration_seconds),
    )
