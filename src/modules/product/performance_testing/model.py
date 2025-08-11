from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.performance_testing.schema import (
    AnalyzePerformanceTestingProgressResponse,
    PerformanceTestCard,
)


class PerformanceTestPlan(Document):
    product_id: str = Field(..., index=True)
    tests: list[PerformanceTestCard] = Field(default_factory=list)
    rationale: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "performance_test_plan"
        use_state_management = True


class AnalyzePerformanceTestingProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_performance_testing_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_performance_testing_progress_response(
        self,
    ) -> AnalyzePerformanceTestingProgressResponse:
        return AnalyzePerformanceTestingProgressResponse(
            product_id=self.product_id,
            total_files=self.total_files,
            processed_files=self.processed_files,
            updated_at=self.updated_at,
            analyzing_status=(
                AnalyzingStatus.IN_PROGRESS
                if self.processed_files == 0
                else AnalyzingStatus.COMPLETED
            ),
        )
