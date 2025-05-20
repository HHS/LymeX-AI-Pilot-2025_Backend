from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.company.models import Company
from src.modules.product.storage import get_product_avatar_url
from src.modules.user.service import get_user_by_id
from src.modules.product.schema import ProductResponse


class Product(Document):
    name: str
    code: str
    model: str
    revision: str
    category: str
    intend_use: str
    patient_contact: bool
    company_id: str
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
    edit_locked: bool = False

    class Settings:
        name = "product"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_product_response(self) -> ProductResponse:
        created_by = await get_user_by_id(self.created_by)
        updated_by = await get_user_by_id(self.updated_by)
        avatar_url = await get_product_avatar_url(self)
        return ProductResponse(
            id=str(self.id),
            code=self.code,
            name=self.name,
            model=self.model,
            revision=self.revision,
            category=self.category,
            avatar_url=avatar_url,
            intend_use=self.intend_use,
            patient_contact=self.patient_contact,
            created_by=await created_by.to_user_response(populate_companies=False),
            created_at=self.created_at,
            updated_by=await updated_by.to_user_response(populate_companies=False),
            updated_at=self.updated_at,
            edit_locked=self.edit_locked,
        )
