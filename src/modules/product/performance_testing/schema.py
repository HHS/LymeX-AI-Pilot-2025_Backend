from datetime import datetime
import enum
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModuleStatus(str, enum.Enum):
    # PENDING = "pending"
    # IN_PROGRESS = "in_progress"
    # COMPLETED = "completed"
    # NEEDS_REVIEW = "needs_review"
    SUGGESTED = "suggested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PerformanceTestingConfidentLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingReference(BaseModel):
    title: str
    url: str | None = None
    description: str | None = None


class PerformanceTestingAssociatedStandard(BaseModel):
    name: str
    standard_name: str | None = None
    version: str | None = None
    url: str | None = None
    description: str | None = None


class PerformanceTestCard(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    product_id: str
    section_key: str
    test_code: str
    test_description: str = "not available"
    status: ModuleStatus = ModuleStatus.SUGGESTED
    risk_level: RiskLevel = RiskLevel.MEDIUM
    ai_confident: int | None = None
    confident_level: PerformanceTestingConfidentLevel | None = None
    ai_rationale: str | None = None
    references: list[PerformanceTestingReference] | None = None
    associated_standards: list[PerformanceTestingAssociatedStandard] | None = None
    rejected_justification: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "ai@crowdplat.com"


class CreatePerformanceTestingRequest(BaseModel):
    test_name: str = Field(
        ...,
        description="Name of the performance test",
    )
    risk_level: str = Field(
        ...,
        description="Risk level of the performance test",
    )
    status: str = Field(
        ...,
        description="Current status of the performance test",
    )
    test_description: str = Field(
        ...,
        description="Description of the performance test",
    )


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
    performance_testing_id: str | None = Field(
        None, description="ID of the associated performance testing"
    )
    content_type: str = Field(
        ..., description="Content type of the document (e.g., PDF, DOCX)"
    )
    size: int = Field(..., description="Size of the document in bytes")


class UploadTextInputDocumentRequest(BaseModel):
    text: str = Field(..., description="Text input for the document")
    performance_testing_id: str | None = Field(
        None, description="ID of the associated performance testing"
    )


class RejectedPerformanceTestingRequest(BaseModel):
    rejected_justification: str


class AnalyzePerformanceTestingProgressResponse(BaseModel):
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


class PerformanceTestingResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the performance test")
    product_id: str = Field(..., description="Associated product identifier")
    test_name: str = Field(..., description="Name of the performance test")
    test_description: str = Field(
        ..., description="Description of the performance test"
    )
    status: ModuleStatus = Field(
        ..., description="Current status of the performance test"
    )
    documents: list[PerformanceTestingDocumentResponse] = Field(
        ..., description="List of documents associated with the performance test"
    )
    risk_level: RiskLevel | None = Field(
        None, description="Risk level of the performance test"
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
    created_at: datetime = Field(
        ..., description="Timestamp when the performance test was created"
    )
    created_by: str = Field(
        ..., description="Email of the user who created the performance test"
    )


class PerformanceTestingWithProgressResponse(BaseModel):
    performance_testing: list[PerformanceTestingResponse] = Field(
        ..., description="List of performance testing results"
    )
    analyze_performance_testing_progress: (
        AnalyzePerformanceTestingProgressResponse | None
    ) = Field(None, description="Progress information for performance testing")


def map_to_performance_testing_response(
    performance_test_card: PerformanceTestCard,
    documents: list[PerformanceTestingDocumentResponse],
) -> PerformanceTestingResponse:
    return PerformanceTestingResponse(
        id=str(performance_test_card.id),
        product_id=performance_test_card.product_id,
        test_name=performance_test_card.section_key,
        test_description=performance_test_card.test_description,
        status=performance_test_card.status,
        documents=[
            document
            for document in documents
            if document.performance_testing_id == str(performance_test_card.id)
        ],
        risk_level=performance_test_card.risk_level,
        ai_confident=performance_test_card.ai_confident,
        confident_level=performance_test_card.confident_level,
        ai_rationale=performance_test_card.ai_rationale,
        references=performance_test_card.references,
        associated_standards=performance_test_card.associated_standards,
        rejected_justification=performance_test_card.rejected_justification,
        created_at=performance_test_card.created_at,
        created_by=performance_test_card.created_by,
    )
