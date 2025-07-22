from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class RegulatoryBackgroundContent(BaseModel):
    title: str = Field(..., description="Title of the regulatory background content")
    content: str = Field(..., description="Content of the regulatory background")
    suggestion: str = Field(..., description="Suggestion for the regulatory background")


class RegulatoryBackgroundBase:
    predicate_device_reference: RegulatoryBackgroundContent
    clinical_trial_requirements: RegulatoryBackgroundContent
    risk_classification: RegulatoryBackgroundContent
    regulatory_submission_history: RegulatoryBackgroundContent
    intended_use_statement: RegulatoryBackgroundContent


class RegulatoryBackground(BaseModel, RegulatoryBackgroundBase): ...


class RegulatoryBackgroundResponse(BaseModel, RegulatoryBackgroundBase):
    id: str = Field(..., description="Unique identifier for the regulatory background")
    product_id: str = Field(
        ..., description="ID of the product this regulatory background belongs to"
    )


class UploadTextInputDocumentRequest(BaseModel):
    text: str | None = Field(None, description="Text input for the document")
    files: list[str] | None = Field(None, description="List of file names to upload")


class RegulatoryBackgroundDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the regulatory background document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")


class AnalyzeRegulatoryBackgroundProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )
