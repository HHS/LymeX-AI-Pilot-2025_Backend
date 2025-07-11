from pydantic import BaseModel, Field


class TestInfo(BaseModel):
    name: str = Field(..., description="Name of the test")
    standard: str = Field(..., description="Standard of the test")
    status: str = Field(..., description="Status of the test")


class IdentifiedGapAndSuggestedAdjustment(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the identified gap and suggested adjustment",
    )
    name: str = Field(
        ..., description="Identified gap and suggested adjustment in the test"
    )
    description: str = Field(
        ..., description="Description of the identified gap and suggested adjustment"
    )
    suggestion: str = Field(
        "",
        description="Suggestion for improvement of the identified gap and suggested adjustment",
    )
    accepted: bool | None = Field(
        None,
        description="Indicates if the identified gap and suggested adjustment is accepted, false is rejected, and null is not yet decided",
    )


# =========== REQUEST SCHEMAS ===========


# =========== RESPONSE SCHEMAS ===========


class TestComparisonResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the test comparison")
    product_id: str = Field(..., description="ID of the product")
    product_name: str = Field(..., description="Name of the product")
    comparison_name: str = Field(..., description="Name of the test comparison")
    requirements: list[TestInfo] = Field(
        ..., description="List of test requirements for the product"
    )
    comparator: list[TestInfo] = Field(
        ..., description="List of comparator test information"
    )
    identified_gaps_and_suggested_adjustments: list[
        IdentifiedGapAndSuggestedAdjustment
    ] = Field(
        ...,
        description="List of identified gaps and suggested adjustments in the test comparison",
    )
