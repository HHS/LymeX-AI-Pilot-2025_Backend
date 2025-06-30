from beanie import PydanticObjectId
from src.modules.product.review_program.model import ReviewProgram
from src.modules.product.review_program.schema import (
    SpecialityProgram,
    ReviewProgramResponse,
)
from src.modules.product.models import Product


async def get_product_review_program(
    product_id: str | PydanticObjectId,
) -> list[ReviewProgramResponse]:
    # Get product data to include name and code
    product = await Product.get(product_id)
    product_name = product.name if product else ""
    product_code = product.code if product else None

    product_review_programs = await ReviewProgram.find(
        {"productId": str(product_id)}
    ).to_list()

    if not product_review_programs:
        # Create dummy data
        dummy_review_program = ReviewProgram(
            productId=str(product_id),
            specialityPrograms=[
                SpecialityProgram(
                    programName="Safer Technologies Program (STeP)",
                    isQualified=True,
                    reason="For devices significantly improving safety of current treatments",
                    description="For devices significantly improving safety of current treatments.",
                    benefits=[
                        "Enhanced communication with FDA",
                        "Prioritized review timeline",
                    ],
                ),
                SpecialityProgram(
                    programName="Humanitarian Use Device (HUD)",
                    isQualified=True,
                    reason="For devices benefiting patients with rare diseases",
                    description="For devices benefiting patients with rare diseases.",
                    benefits=[
                        "Modified regulatory requirements",
                        "Special market incentives",
                    ],
                ),
                SpecialityProgram(
                    programName="Breakthrough Device Designation",
                    isQualified=False,
                    reason="For devices that provide more effective treatment of life-threatening conditions",
                    description="For devices that provide more effective treatment of life-threatening conditions.",
                    benefits=[
                        "Expedited development and review",
                        "Interactive and priority review",
                    ],
                ),
            ],
        )

        # Save to database
        await dummy_review_program.save()

        # Return with product data
        return [
            ReviewProgramResponse(
                productId=str(product_id),
                product_name=product_name,
                product_code=product_code,
                specialityPrograms=dummy_review_program.specialityPrograms,
            )
        ]

    # Convert existing programs to response format with product data
    return [
        ReviewProgramResponse(
            productId=program.productId,
            product_name=product_name,
            product_code=product_code,
            specialityPrograms=program.specialityPrograms,
        )
        for program in product_review_programs
    ]
