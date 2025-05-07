from pydantic import BaseModel, Field


class UploadDocumentUrlResponse(BaseModel):
    url: str = Field(..., description="Presigned URL for uploading a file")


class GetDocumentResponse(BaseModel):
    name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="Presigned URL for downloading the document")
