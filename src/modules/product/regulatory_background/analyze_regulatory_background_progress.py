


from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.regulatory_background.schema import AnalyzeRegulatoryBackgroundProgressResponse


class AnalyzeRegulatoryBackgroundProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_regulatory_background_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_regulatory_background_progress_response(
        self,
    ) -> AnalyzeRegulatoryBackgroundProgressResponse:
        return AnalyzeRegulatoryBackgroundProgressResponse(
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
    

async def get_analyze_regulatory_background_progress(
    product_id: str,
) -> AnalyzeRegulatoryBackgroundProgress | None:
    analyze_regulatory_background_progress = (
        await AnalyzeRegulatoryBackgroundProgress.find_one(
            AnalyzeRegulatoryBackgroundProgress.product_id == str(product_id),
        )
    )
    if not analyze_regulatory_background_progress:
        return None
    return analyze_regulatory_background_progress