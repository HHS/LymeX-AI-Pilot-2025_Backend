from beanie import PydanticObjectId
from src.modules.product.review_program.model import ReviewProgram
from src.modules.product.review_program.schema import SpecialityProgram


async def get_product_review_program(
    product_id: str | PydanticObjectId,
) -> list[ReviewProgram]:
    product_review_programs = await ReviewProgram.find(
        {"productId": str(product_id)}
    ).to_list()

    if not product_review_programs:
        # Create dummy data
        dummy_review_program = ReviewProgram(
            productId=str(product_id),
            specialityPrograms=[
                SpecialityProgram(
                    programName="HUD",
                    isQualified=True,
                    reason="Because it is used for certain section of people with disabilities it can be qualified under HUD Program",
                ),
                SpecialityProgram(
                    programName="Etap",
                    isQualified=False,
                    reason="It is not qualified under this program because it is not a breakthrough technology already exist in market",
                ),
                SpecialityProgram(
                    programName="Breakthrough Device",
                    isQualified=False,
                    reason="The technology does not meet the breakthrough device criteria as it is not significantly more effective than existing alternatives",
                ),
            ],
        )
        # Save to database
        await dummy_review_program.save()
        return [dummy_review_program]

    return product_review_programs
