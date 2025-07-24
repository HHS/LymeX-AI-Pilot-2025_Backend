from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.performance_testing.schema import (
    PerformanceTestingConfidentLevel,
    PerformanceTestingResponse,
    PerformanceTestingStatus,
    PerformanceTestingRiskLevel,
    PerformanceTestingReference,
    PerformanceTestingAssociatedStandard,
    AnalyzePerformanceTestingProgressResponse,
)


class PerformanceTesting(Document):
    product_id: str
    test_name: str
    test_description: str
    status: PerformanceTestingStatus
    risk_level: PerformanceTestingRiskLevel
    ai_confident: int | None = None
    confident_level: PerformanceTestingConfidentLevel | None = None
    ai_rationale: str | None = None
    references: list[PerformanceTestingReference] | None = None
    associated_standards: list[PerformanceTestingAssociatedStandard] | None = None
    rejected_justification: str | None = None

    class Settings:
        name = "performance_testing"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_performance_testing_response(self) -> PerformanceTestingResponse:
        return PerformanceTestingResponse(
            id=str(self.id),
            product_id=self.product_id,
            test_name=self.test_name,
            test_description=self.test_description,
            status=self.status,
            risk_level=self.risk_level,
            ai_confident=self.ai_confident,
            confident_level=self.confident_level,
            ai_rationale=self.ai_rationale,
            references=self.references,
            associated_standards=self.associated_standards,
            rejected_justification=self.rejected_justification,
        )


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
