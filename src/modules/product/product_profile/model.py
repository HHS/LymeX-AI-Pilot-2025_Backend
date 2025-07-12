from datetime import datetime
from typing import Any

from beanie import Document, PydanticObjectId

from src.modules.product.models import Product
from src.modules.product.product_profile.schema import (
    AnalyzeProductProfileProgressResponse,
    AnalyzingStatus,
    Feature,
    Performance,
    ProductProfileAnalysisResponse,
    ProductProfileAuditResponse,
    ProductProfileResponse,
    RegulatoryClassification,
)
from src.modules.product.schema import ProductResponse


class ProductProfile(Document):
    product_id: str
    reference_number: str
    description: str
    regulatory_pathway: str
    regulatory_classifications: list[RegulatoryClassification]
    device_description: str
    features: list[Feature]
    claims: list[str]
    conflict_alerts: list[str]
    fda_approved: bool | None
    ce_marked: bool | None
    device_ifu_description: str
    confidence_score: float
    sources: list[str]
    performance: Performance
    price: int | None
    instructions: list[str]
    type_of_use: str

    class Settings:
        name = "product_profile"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_product_profile_response(
        self,
        product_response: ProductResponse | None,
        analyze_progress: AnalyzeProductProfileProgressResponse | None,
    ) -> ProductProfileResponse:
        product_response = (
            {
                "name": product_response.name,
                "model": product_response.model,
                "revision": product_response.revision,
                "category": product_response.category,
                "avatar_url": product_response.avatar_url,
                "intend_use": product_response.intend_use,
                "patient_contact": product_response.patient_contact,
                "created_by": product_response.created_by,
                "created_at": product_response.created_at,
                "updated_by": product_response.updated_by,
                "updated_at": product_response.updated_at,
                "edit_locked": product_response.edit_locked,
            }
            if product_response
            else {}
        )
        return ProductProfileResponse(
            id=str(self.id),
            product_id=self.product_id,
            description=self.description,
            regulatory_classifications=self.regulatory_classifications,
            device_description=self.device_description,
            features=self.features,
            claims=self.claims,
            conflict_alerts=self.conflict_alerts,
            analyzing_status=(
                analyze_progress.analyzing_status
                if analyze_progress
                else AnalyzingStatus.PENDING
            ),
            **product_response,
        )

    def to_product_profile_analysis_response(
        self,
        product: Product,
        analyze_progress: AnalyzeProductProfileProgressResponse | None = None,
    ) -> ProductProfileAnalysisResponse:
        return ProductProfileAnalysisResponse(
            product_id=str(product.id),
            product_code=product.code,
            product_name=product.name,
            updated_at=product.updated_at,
            fda_approved=self.fda_approved,
            ce_marked=self.ce_marked,
            features=self.features,
            regulatory_classifications=self.regulatory_classifications,
            analyzing_status=(
                analyze_progress.analyzing_status
                if analyze_progress
                else AnalyzingStatus.PENDING
            ),
        )


class ProductProfileAudit(Document):
    product_id: str
    product_name: str | None = None
    user_id: str
    user_email: str
    user_name: str | None = None
    action: str
    data: Any
    timestamp: datetime

    def to_product_profile_audit_response(
        self,
        version: str,
    ) -> ProductProfileAuditResponse:
        return ProductProfileAuditResponse(
            product_id=self.product_id,
            product_name=self.product_name,
            user_id=self.user_id,
            user_email=self.user_email,
            user_name=self.user_name,
            action=self.action,
            data=self.data,
            timestamp=self.timestamp,
            version=version,
        )
