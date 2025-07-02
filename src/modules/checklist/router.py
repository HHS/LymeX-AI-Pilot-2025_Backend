from fastapi import APIRouter, UploadFile, File, HTTPException
import io
from src.infrastructure.minio import minio_client, generate_get_object_presigned_url
from src.environment import environment

def get_checklist_folder(product_id: str) -> str:
    return f"product/{product_id}/checklist"

router = APIRouter()

@router.post("/upload-image")
async def upload_checklist_image(product_id: str, file: UploadFile = File(...)):
    try:
        for bucket in minio_client.list_buckets():
            print("Existing bucket:", bucket.name)

        object_name = f"{get_checklist_folder(product_id)}/{file.filename}"
        file_content = await file.read()
        minio_client.put_object(
            bucket_name=environment.minio_bucket,
            object_name=object_name,
            data=io.BytesIO(file_content),
            length=len(file_content),
            content_type=file.content_type,
        )
        url = await generate_get_object_presigned_url(object_name)
        return {"object_name": object_name, "url": url, "message": "Image uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
