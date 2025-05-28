from datetime import datetime
from pydantic import BaseModel, Field


class TestInfo(BaseModel):
    name: str = Field(..., description="Name of the test")
    standard: str = Field(..., description="Standard of the test")
    status: str = Field(..., description="Status of the test")


class IdentifiedGap(BaseModel):
    name: str = Field(..., description="Identified gap in the test")
    description: str = Field(..., description="Description of the identified gap")


class SuggestedAdjustment(BaseModel):
    name: str = Field(..., description="Suggested adjustment for the identified gap")
    description: str = Field(..., description="Description of the suggested adjustment")


# =========== REQUEST SCHEMAS ===========


class CreateTestComparisonNoteRequest(BaseModel):
    note: str = Field(..., description="Note for the test comparison analysis")


# =========== RESPONSE SCHEMAS ===========


class TestComparisonResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    requirements: list[TestInfo] = Field(
        ..., description="List of test requirements for the product"
    )
    comparator: list[TestInfo] = Field(
        ..., description="List of comparator test information"
    )
    identified_gaps: list[IdentifiedGap] = Field(
        ..., description="List of identified gaps in the test"
    )
    suggested_adjustments: list[SuggestedAdjustment] = Field(
        ..., description="List of suggested adjustments for the identified gaps"
    )


class TestComparisonNoteResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    note: str = Field(..., description="Note for the test comparison analysis")
    updated_at: datetime = Field(
        ..., description="Timestamp of when the note was last updated"
    )
    updated_by: str = Field(..., description="ID of the user who last updated the note")


class UploadTestComparisonNoteDocumentUrlResponse(BaseModel):
    upload_url: str = Field(
        ...,
        description="Presigned URL for uploading the test comparison note document",
    )


class GetTestComparisonNoteDocumentUrlsResponse(BaseModel):
    document_urls: list[str] = Field(
        ...,
        description="List of presigned URLs for downloading test comparison note documents",
    )
