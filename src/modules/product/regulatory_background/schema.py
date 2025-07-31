from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class RegulatoryBackgroundHighlight(BaseModel):
    title: str
    detail: str


class RegulatoryBackgroundSummary(BaseModel):
    title: str
    description: str
    highlights: list[RegulatoryBackgroundHighlight]


class RegulatoryBackgroundFinding(BaseModel):
    status: str
    field: str
    label: str
    value: str
    source_file: str | None
    source_page: int | None
    suggestion: str | None
    tooltip: str | None
    confidence_score: int | None
    user_action: bool | None


class RegulatoryBackgroundConflict(BaseModel):
    field: str
    phrase: str
    conflict: str
    source: str
    suggestion: str
    user_action: bool | None = None


class RegulatoryBackgroundBase:
    summary: RegulatoryBackgroundSummary
    findings: list[RegulatoryBackgroundFinding]
    conflicts: list[RegulatoryBackgroundConflict]


class RegulatoryBackgroundSchema(BaseModel, RegulatoryBackgroundBase): ...


class RegulatoryBackgroundResponse(BaseModel, RegulatoryBackgroundBase):
    id: str = Field(..., description="Unique identifier for the regulatory background")
    product_id: str = Field(
        ..., description="ID of the product this regulatory background belongs to"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
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
