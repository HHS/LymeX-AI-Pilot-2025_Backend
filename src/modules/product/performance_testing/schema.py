from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class PerformanceTestingStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    SUGGESTED = "Suggested"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class PerformanceTestingRiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingConfidentLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingReference(BaseModel):
    title: str = Field(..., description="Title of the reference")
    url: str = Field(..., description="URL of the reference")
    description: str = Field("", description="Description of the reference")


class PerformanceTestingAssociatedStandard(BaseModel):
    name: str = Field(..., description="Name of the associated standard + version")
    standard_name: str = Field(..., description="Name of the associated standard")
    version: str = Field(..., description="Version of the associated standard")
    url: str = Field(..., description="URL of the associated standard")
    description: str = Field("", description="Description of the associated standard")


# ============ REQUEST SCHEMAS ============


class CreatePerformanceTestingRequest(BaseModel):
    test_name: str = Field(
        ...,
        description="Name of the performance test",
    )
    risk_level: PerformanceTestingRiskLevel = Field(
        ...,
        description="Risk level of the performance test",
    )
    status: PerformanceTestingStatus = Field(
        ...,
        description="Current status of the performance test",
    )
    test_description: str = Field(
        ...,
        description="Description of the performance test",
    )


# ============ REQUEST SCHEMAS ============


class RejectedPerformanceTestingRequest(BaseModel):
    rejected_justification: str


# ============ RESPONSE SCHEMAS ============


class PerformanceTestingResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the performance test")
    product_id: str = Field(..., description="Associated product identifier")
    test_name: str = Field(..., description="Name of the performance test")
    test_description: str = Field(
        ..., description="Description of the performance test"
    )
    status: PerformanceTestingStatus = Field(
        ..., description="Current status of the performance test"
    )
    risk_level: PerformanceTestingRiskLevel | None = (
        Field(None, description="Risk level of the performance test"),
    )
    ai_confident: int | None = Field(
        None, description="AI confidence score for the performance test"
    )
    confident_level: PerformanceTestingConfidentLevel | None = Field(
        None, description="Confidence level of the performance test results"
    )
    ai_rationale: str | None = Field(
        None, description="AI rationale for the performance test results"
    )
    references: list[PerformanceTestingReference] | None = Field(
        None, description="List of references for the performance test"
    )
    associated_standards: list[PerformanceTestingAssociatedStandard] | None = Field(
        None, description="List of associated standards for the performance test"
    )
    rejected_justification: str | None = Field(
        None, description="Justification for rejection, if applicable"
    )


class UploadTextInputDocumentRequest(BaseModel):
    text: str = Field(..., description="Text input for the document")


class PerformanceTestingDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the performance testing document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    content_type: str = Field(
        ..., description="Content type of the document (e.g., PDF, DOCX)"
    )
    size: int = Field(..., description="Size of the document in bytes")


class AnalyzePerformanceTestingProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the reference product")
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
