from beanie import PydanticObjectId
from src.modules.product.cost_estimation.model import CostEstimation
from src.modules.product.cost_estimation.schema import (
    Pathway,
    CostAnalysis,
    SaveCostEstimationRequest,
    CostEstimationResponse,
)
from src.modules.product.models import Product


async def get_product_cost_estimation(
    product_id: str | PydanticObjectId,
) -> list[CostEstimationResponse]:
    # Get product data to include name and code
    product = await Product.get(product_id)
    product_name = product.name if product else ""
    product_code = product.code if product else None

    product_cost_estimations = await CostEstimation.find(
        {"product_id": str(product_id)}
    ).to_list()

    if not product_cost_estimations:
        # Create dummy data
        dummy_cost_estimation = CostEstimation(
            product_id=str(product_id),
            can_apply_for_sbd=True,
            pathways=[
                Pathway(
                    pathway="510(k)",
                    costAnalysis=CostAnalysis(
                        sbd_fee_reduction="6084",
                        estimated_consulting_costs="10",
                        clinical_trial_costs="10",
                        total_estimated_cost="6104",
                    ),
                ),
                Pathway(
                    pathway="DeNovo",
                    costAnalysis=CostAnalysis(
                        sbd_fee_reduction="43446",
                        estimated_consulting_costs="10",
                        clinical_trial_costs="10",
                        total_estimated_cost="43466",
                    ),
                ),
                Pathway(
                    pathway="PMA",
                    costAnalysis=CostAnalysis(
                        sbd_fee_reduction="144818",
                        estimated_consulting_costs="10",
                        clinical_trial_costs="10",
                        total_estimated_cost="144838",
                    ),
                ),
            ],
        )
        # Save to database
        await dummy_cost_estimation.save()

        # Return with product data using model method
        return [
            dummy_cost_estimation.to_cost_estimation_response(
                product_name, product_code
            )
        ]

    # Convert existing estimations to response format with product data using model method
    return [
        estimation.to_cost_estimation_response(product_name, product_code)
        for estimation in product_cost_estimations
    ]


async def save_product_cost_estimation(
    product_id: str | PydanticObjectId, cost_estimation: SaveCostEstimationRequest
) -> CostEstimation:
    # Find existing cost estimation for the product
    existing_estimation = await CostEstimation.find_one({"product_id": str(product_id)})

    if existing_estimation:
        # Update existing pathways
        for i, pathway in enumerate(existing_estimation.pathways):
            if pathway.pathway == cost_estimation.pathway:
                existing_estimation.pathways[i] = cost_estimation
                break
        else:
            # If pathway doesn't exist, append it
            existing_estimation.pathways.append(cost_estimation)

        await existing_estimation.save()
        return existing_estimation

    # Create new cost estimation if none exists
    new_estimation = CostEstimation(
        product_id=str(product_id),
        can_apply_for_sbd=True,  # Default value, can be updated later
        pathways=[cost_estimation],
    )
    await new_estimation.save()
    return new_estimation


async def clone_cost_estimation(
    product_id: str | PydanticObjectId,
    new_product_id: str | PydanticObjectId,
) -> None:
    existing_estimation = await CostEstimation.find(
        CostEstimation.product_id == str(product_id)
    ).to_list()
    if existing_estimation:
        await CostEstimation.insert_many(
            [
                CostEstimation(
                    **estimation.model_dump(exclude={"id", "product_id"}),
                    product_id=str(new_product_id),
                )
                for estimation in existing_estimation
            ]
        )
