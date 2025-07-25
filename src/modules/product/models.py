from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.company.models import Company
from src.modules.product.claim_builder.service import get_analyze_claim_builder_progress
from src.modules.product.competitive_analysis.service import (
    get_analyze_competitive_analysis_progress,
)
from src.modules.product.performance_testing.service import (
    get_analyze_performance_testing_progress,
)
from src.modules.product.product_profile.analyze_product_profile_progress import (
    get_analyze_product_profile_progress,
)
from src.modules.product.analyzing_status import AnalyzingStatus
from src.modules.product.regulatory_pathway.service import (
    get_analyze_regulatory_pathway_progress,
)
from src.modules.product.storage import get_product_avatar_url
from src.modules.user.service import get_user_by_id
from src.modules.product.schema import ProductResponse


class Product(Document):
    name: str
    code: str | None = None
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

    regulatory_background_percentage: float = Field(default=0.0, ge=0, le=100)
    claims_builder_percentage: float = Field(default=0.0, ge=0, le=100)
    competitive_analysis_percentage: float = Field(default=0.0, ge=0, le=100)
    standards_guidance_documents_percentage: float = Field(default=0.0, ge=0, le=100)
    performance_testing_requirements_percentage: float = Field(
        default=0.0, ge=0, le=100
    )
    regulatory_pathway_analysis_percentage: float = Field(default=0.0, ge=0, le=100)

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

        # Calculate is_active_profile using the same logic as get_active_products
        is_active_profile = False
        try:
            # Get the company to check for active_product_id
            company = await Company.get(self.company_id)
            if company:
                # 0. HIGHEST PRECEDENCE: Check if company has an active product set
                if company.active_product_id:
                    is_active_profile = str(self.id) == company.active_product_id
                else:
                    # If no active product set, check if this is the most recently updated product
                    # Get all products for this company
                    from src.modules.product.models import Product

                    products = await Product.find(
                        Product.company_id == self.company_id,
                    ).to_list()

                    if products:
                        # Find the most recently updated product
                        most_recent_product = max(products, key=lambda p: p.updated_at)
                        is_active_profile = self.id == most_recent_product.id
        except Exception as e:
            # If there's any error, default to False
            print(f"Error calculating is_active_profile for product {self.id}: {e}")
            is_active_profile = False

        # Fetch product profile data (using dynamic import to avoid circular import)
        try:
            from src.modules.product.product_profile.model import (
                ProductProfile,
            )

            product_profile = await ProductProfile.find_one(
                ProductProfile.product_id == str(self.id)
            )
            # Extract product profile fields
            description = product_profile.description if product_profile else None
            fda_approved = product_profile.fda_approved if product_profile else None
            ce_marked = product_profile.ce_marked if product_profile else None
            # Extract additional product profile fields
            reference_number = (
                product_profile.reference_number if product_profile else None
            )
            regulatory_pathway = (
                product_profile.regulatory_pathway if product_profile else None
            )
            regulatory_classifications = (
                [rc.model_dump() for rc in product_profile.regulatory_classifications]
                if product_profile and product_profile.regulatory_classifications
                else None
            )
            device_description = (
                product_profile.device_description if product_profile else None
            )
            features = (
                [feature.model_dump() for feature in product_profile.features]
                if product_profile and product_profile.features
                else None
            )
            claims = product_profile.claims if product_profile else None
            conflict_alerts = (
                product_profile.conflict_alerts if product_profile else None
            )
            device_ifu_description = (
                product_profile.device_ifu_description if product_profile else None
            )
            confidence_score = (
                product_profile.confidence_score if product_profile else None
            )
            sources = product_profile.sources if product_profile else None
            performance = (
                {
                    "speed": product_profile.speed,
                    "reliability": product_profile.reliability,
                }
                if product_profile
                and product_profile.speed
                and product_profile.reliability
                else None
            )
            price = product_profile.price if product_profile else None
            instructions = product_profile.instructions if product_profile else None
            type_of_use = product_profile.type_of_use if product_profile else None
        except ImportError:
            # Fallback if import fails
            description = None
            fda_approved = None
            ce_marked = None
            # Additional product profile fields fallback
            reference_number = None
            regulatory_pathway = None
            regulatory_classifications = None
            device_description = None
            features = None
            claims = None
            conflict_alerts = None
            device_ifu_description = None
            confidence_score = None
            sources = None
            performance = None
            price = None
            instructions = None
            type_of_use = None

        analyze_claim_builder_progress = await get_analyze_claim_builder_progress(
            str(self.id),
        )
        analyze_claim_builder_progress_status = (
            analyze_claim_builder_progress.to_analyze_claim_builder_progress_response().analyzing_status
            if analyze_claim_builder_progress
            else AnalyzingStatus.PENDING
        )

        analyze_competitive_analysis_progress = (
            await get_analyze_competitive_analysis_progress(
                str(self.id),
            )
        )
        analyze_competitive_analysis_progress_status = (
            analyze_competitive_analysis_progress.to_analyze_competitive_analysis_progress_response().analyzing_status
            if analyze_competitive_analysis_progress
            else AnalyzingStatus.PENDING
        )

        analyze_product_profile_progress = await get_analyze_product_profile_progress(
            str(self.id),
        )
        analyze_product_profile_progress_status = (
            analyze_product_profile_progress.to_analyze_product_profile_progress_response().analyzing_status
            if analyze_product_profile_progress
            else AnalyzingStatus.PENDING
        )

        analyze_regulatory_pathway_progress = (
            await get_analyze_regulatory_pathway_progress(str(self.id))
        )
        analyze_regulatory_pathway_progress_status = (
            analyze_regulatory_pathway_progress.to_analyze_regulatory_pathway_progress_response().analyzing_status
            if analyze_regulatory_pathway_progress
            else AnalyzingStatus.PENDING
        )

        analyze_performance_testing_progress = (
            await get_analyze_performance_testing_progress(str(self.id))
        )
        analyze_performance_testing_progress_status = (
            analyze_performance_testing_progress.to_analyze_performance_testing_progress_response().analyzing_status
            if analyze_performance_testing_progress
            else AnalyzingStatus.PENDING
        )

        is_analyzing_complete = (
            analyze_competitive_analysis_progress_status == AnalyzingStatus.COMPLETED
            and analyze_claim_builder_progress_status == AnalyzingStatus.COMPLETED
            and analyze_product_profile_progress_status == AnalyzingStatus.COMPLETED
            and analyze_regulatory_pathway_progress_status == AnalyzingStatus.COMPLETED
            and analyze_performance_testing_progress_status == AnalyzingStatus.COMPLETED
        )

        print(
            f"Product [{self.id}] - analyze_claim_builder_progress_status: {analyze_claim_builder_progress_status}"
        )
        print(
            f"Product [{self.id}] - analyze_competitive_analysis_progress_status: {analyze_competitive_analysis_progress_status}"
        )
        print(
            f"Product [{self.id}] - analyze_product_profile_progress_status: {analyze_product_profile_progress_status}"
        )
        print(
            f"Product [{self.id}] - analyze_regulatory_pathway_progress_status: {analyze_regulatory_pathway_progress_status}"
        )
        print(
            f"Product [{self.id}] - analyze_performance_testing_progress_status: {analyze_performance_testing_progress_status}"
        )

        analyzing_status = (
            AnalyzingStatus.COMPLETED
            if is_analyzing_complete
            else AnalyzingStatus.IN_PROGRESS
        )

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
            updated_at=self.updated_at,
            edit_locked=self.edit_locked,
            is_active_profile=is_active_profile,
            analyzing_status=analyzing_status,
            # Product Profile fields
            description=description,
            fda_approved=fda_approved,
            ce_marked=ce_marked,
            # Additional Product Profile fields
            reference_number=reference_number,
            regulatory_pathway=regulatory_pathway,
            regulatory_classifications=regulatory_classifications,
            device_description=device_description,
            features=features,
            claims=claims,
            conflict_alerts=conflict_alerts,
            device_ifu_description=device_ifu_description,
            confidence_score=confidence_score,
            sources=sources,
            performance=performance,
            price=price,
            instructions=instructions,
            type_of_use=type_of_use,
            created_by=await created_by.to_user_response(populate_companies=False),
            created_at=self.created_at,
            updated_by=await updated_by.to_user_response(populate_companies=False),
        )
