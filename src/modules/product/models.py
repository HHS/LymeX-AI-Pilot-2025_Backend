from datetime import datetime
from typing import Annotated, Optional
from beanie import Document, Indexed, PydanticObjectId

from src.modules.product.constants import ProductStatus
from src.modules.user.service import get_user_by_id
from src.modules.product.schema import ProductResponse


class Product(Document):
    code: str
    name: str
    model: str
    revision: str
    description: str
    intend_use: str
    patient_contact: bool
    device_description: str
    key_features: str
    category: str
    version: str
    is_latest: bool
    status: ProductStatus
    company_id: str
    created_by: str
    created_at: datetime
    edit_locked: bool = False

    class Settings:
        name = "product"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_product_response(self) -> ProductResponse:
        created_by = await get_user_by_id(self.created_by)
        return ProductResponse(
            id=str(self.id),
            code=self.code,
            name=self.name,
            model=self.model,
            revision=self.revision,
            description=self.description,
            intend_use=self.intend_use,
            patient_contact=self.patient_contact,
            device_description=self.device_description,
            key_features=self.key_features,
            category=self.category,
            version=self.version,
            is_latest=self.is_latest,
            status=self.status,
            created_by=await created_by.to_user_response(),
            created_at=self.created_at,
        )
