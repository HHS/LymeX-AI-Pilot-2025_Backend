from beanie import Document
from typing import List
from src.modules.product.review_program.schema import SpecialityProgram


class ReviewProgram(Document):
    productId: str
    specialityPrograms: List[SpecialityProgram]

    class Settings:
        name = "review_programs"

    def to_review_program_response(self):
        return {
            "productId": self.productId,
            "specialityPrograms": self.specialityPrograms,
        }
