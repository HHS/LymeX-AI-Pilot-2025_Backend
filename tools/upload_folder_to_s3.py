from minio import Minio
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from loguru import logger


class Environment(BaseSettings):
    # MINIO CONFIGURATION
    minio_internal_endpoint: str
    minio_root_user: str
    minio_root_password: str
    minio_bucket: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


environment = Environment()


minio_client = Minio(
    environment.minio_internal_endpoint.removeprefix("http://").removeprefix(
        "https://"
    ),
    access_key=environment.minio_root_user,
    secret_key=environment.minio_root_password,
    secure=environment.minio_internal_endpoint.startswith("https://"),
)


def upload_folder_to_minio(folder_path: str, prefix: str = ""):
    """
    Uploads all files (non-recursive) from the given folder to MinIO,
    using the specified prefix. Keeps the original file name and extension.
    """
    folder = Path(folder_path)
    logger.info(
        f"Starting upload of files from folder: {folder_path} to bucket: {environment.minio_bucket} with prefix: '{prefix}'"
    )
    for file_path in folder.iterdir():
        if file_path.is_file():
            object_name = f"{prefix}{file_path.name}" if prefix else file_path.name
            logger.info(f"Uploading file: {file_path} as object: {object_name}")
            try:
                with file_path.open("rb") as file_data:
                    minio_client.put_object(
                        environment.minio_bucket,
                        object_name,
                        file_data,
                        length=file_path.stat().st_size,
                    )
                logger.success(f"Successfully uploaded: {file_path} to {object_name}")
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
    logger.info("Upload process completed.")


def get_objects_by_prefix(prefix: str) -> list[str]:
    """
    Retrieves a list of objects from the MinIO bucket that match the given prefix.
    """
    objects = []
    try:
        for obj in minio_client.list_objects(
            environment.minio_bucket, prefix=prefix, recursive=True
        ):
            objects.append(obj.object_name)
    except Exception as e:
        logger.error(f"Failed to retrieve objects with prefix {prefix}: {e}")
    return objects


if __name__ == "__main__":
    upload_folder_to_minio(
        "/Users/macbookpro/Documents/NOIS2_192_DATA/shards",
        "clinical_trial_data/shards/",
    )
    objects = get_objects_by_prefix("clinical_trial_data/shards/")
    for obj in objects:
        logger.info(f"Found object: {obj}")
