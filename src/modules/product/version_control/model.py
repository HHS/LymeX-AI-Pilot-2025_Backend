from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.product.version_control.schema import ProductVersionControlResponse


class ProductVersionControl(Document):
    product_id: str
    major_version: int
    minor_version: int
    comment: str
    created_at: datetime
    created_by: str

    class Settings:
        name = "product_version_control"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_product_version_control_response(self) -> ProductVersionControlResponse:
        return ProductVersionControlResponse(
            version=f"v{self.major_version}.{self.minor_version}",
            comment=self.comment,
            created_at=self.created_at.isoformat(),
            created_by=self.created_by,
        )
