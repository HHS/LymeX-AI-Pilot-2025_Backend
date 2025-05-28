from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.product.test_comparison.schema import (
    IdentifiedGap,
    SuggestedAdjustment,
    TestComparisonNoteResponse,
    TestComparisonResponse,
    TestInfo,
)


class TestComparison(Document):
    product_id: str
    requirements: list[TestInfo]
    comparator: list[TestInfo]
    identified_gaps: list[IdentifiedGap]
    suggested_adjustments: list[SuggestedAdjustment]

    class Settings:
        name = "test_comparison"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_test_comparison_response(self) -> TestComparisonResponse:
        return TestComparisonResponse(
            product_id=self.product_id,
            requirements=self.requirements,
            comparator=self.comparator,
            identified_gaps=self.identified_gaps,
            suggested_adjustments=self.suggested_adjustments,
        )


class TestComparisonNote(Document):
    product_id: str
    note: str
    updated_at: datetime
    updated_by: str

    class Settings:
        name = "test_comparison_note"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_test_comparison_note_response(self) -> TestComparisonNoteResponse:
        return TestComparisonNoteResponse(
            product_id=self.product_id,
            note=self.note,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
        )
