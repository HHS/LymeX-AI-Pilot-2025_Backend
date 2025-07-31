from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.competitive_analysis.schema import (
    AnalyzeCompetitiveAnalysisProgressResponse,
)


class AnalyzeCompetitiveAnalysisProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_competitive_analysis_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_competitive_analysis_progress_response(
        self,
    ) -> AnalyzeCompetitiveAnalysisProgressResponse:
        return AnalyzeCompetitiveAnalysisProgressResponse(
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


async def get_analyze_competitive_analysis_progress(
    product_id: str,
) -> AnalyzeCompetitiveAnalysisProgress | None:
    analyze_competitive_analysis_progress = (
        await AnalyzeCompetitiveAnalysisProgress.find_one(
            AnalyzeCompetitiveAnalysisProgress.product_id == str(product_id),
        )
    )
    if not analyze_competitive_analysis_progress:
        return None
    return analyze_competitive_analysis_progress


