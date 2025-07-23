from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.product_profile.schema import (
    AnalyzeProductProfileProgressResponse,
    AnalyzingStatus,
)


class AnalyzeProductProfileProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_product_profile_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_analyze_product_profile_progress_response(
        self,
    ) -> AnalyzeProductProfileProgressResponse:
        return AnalyzeProductProfileProgressResponse(
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


async def get_analyze_product_profile_progress(
    product_id: str | PydanticObjectId,
) -> AnalyzeProductProfileProgress | None:
    analyze_product_profile_progress = await AnalyzeProductProfileProgress.find_one(
        AnalyzeProductProfileProgress.product_id == str(product_id),
    )
    if not analyze_product_profile_progress:
        return None
    return analyze_product_profile_progress
