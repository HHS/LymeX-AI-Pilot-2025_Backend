from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.product.models import Product
from src.modules.product.schema import ProductResponse
from src.modules.product.product_profile.schema import (
    AnalyzeProductProfileProgressResponse,
    Feature,
    Performance,
    ProductProfileAnalysisResponse,
    ProductProfileResponse,
    RegulatoryClassification,
)


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
    fda_approved: bool
    ce_marked: bool
    device_ifu_description: str
    confidence_score: float
    sources: list[str]
    performance: Performance
    price: int

    class Settings:
        name = "product_profile"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_product_profile_response(
        self, product_response: ProductResponse | None
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
            **product_response,
        )

    def to_product_profile_analysis_response(
        self, product: Product
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
        return {
            "product_id": self.product_id,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "updated_at": self.updated_at,
        }
