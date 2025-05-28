from beanie import Document, PydanticObjectId

from src.modules.product.regulatory_pathway.schema import (
    AlternativePathway,
    RegulatoryPathwayJustification,
    RegulatoryPathwayResponse,
)


class RegulatoryPathway(Document):
    product_id: str
    recommended_pathway: str
    confident_score: int
    description: str
    estimated_time_days: int
    alternative_pathways: list[AlternativePathway]
    justifications: list[RegulatoryPathwayJustification]
    supporting_documents: list[str]

    class Settings:
        name = "regulatory_pathway"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def to_regulatory_pathway_response(self) -> RegulatoryPathwayResponse:
        return RegulatoryPathwayResponse(
            product_id=self.product_id,
            recommended_pathway=self.recommended_pathway,
            confident_score=self.confident_score,
            description=self.description,
            estimated_time_days=self.estimated_time_days,
            alternative_pathways=self.alternative_pathways,
            justifications=self.justifications,
            supporting_documents=self.supporting_documents,
        )
