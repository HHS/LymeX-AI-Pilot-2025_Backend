from beanie import Document, PydanticObjectId

from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.models import Product
from src.modules.product.regulatory_background.analyze_regulatory_background_progress import (
    get_analyze_regulatory_background_progress,
)
from src.modules.product.regulatory_background.schema import (
    RegulatoryBackgroundBase,
    RegulatoryBackgroundResponse,
)


class RegulatoryBackground(Document, RegulatoryBackgroundBase):
    product_id: str

    class Settings:
        name = "regulatory_background"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_regulatory_background_response(
        self, product: Product,
    ) -> RegulatoryBackgroundResponse:
        analyze_regulatory_background_progress = (
            await get_analyze_regulatory_background_progress(
                self.product_id,
            )
        )

        analyze_regulatory_background_progress_status = (
            analyze_regulatory_background_progress.to_analyze_regulatory_background_progress_response().analyzing_status
            if analyze_regulatory_background_progress
            else AnalyzingStatus.PENDING
        )
        return RegulatoryBackgroundResponse(
            id=str(self.id),
            product_id=self.product_id,
            product_name=product.name,
            summary=self.summary,
            findings=self.findings,
            conflicts=self.conflicts,
            analyzing_status=analyze_regulatory_background_progress_status,
        )
