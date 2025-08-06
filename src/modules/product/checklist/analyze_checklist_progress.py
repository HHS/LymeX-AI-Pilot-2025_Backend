from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.checklist.schema import (
    AnalyzeChecklistProgressResponse,
    AnalyzingStatus,
)


class AnalyzeChecklistProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_checklist_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_checklist_progress_response(
        self,
    ) -> AnalyzeChecklistProgressResponse:
        return AnalyzeChecklistProgressResponse(
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


async def get_analyze_checklist_progress(
    product_id: str | PydanticObjectId,
) -> AnalyzeChecklistProgress | None:
    analyze_checklist_progress = await AnalyzeChecklistProgress.find_one(
        AnalyzeChecklistProgress.product_id == str(product_id),
    )
    if not analyze_checklist_progress:
        return None
    return analyze_checklist_progress
