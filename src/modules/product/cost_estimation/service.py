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
                        base_mdufa_fee="19870",
                        sbd_fee_reduction="14902",
                        estimated_consulting_costs="10",
                        clinical_trial_costs="10",
                        total_estimated_cost="4968",
                    ),
                ),
                Pathway(
                    pathway="DeNovo",
                    costAnalysis=CostAnalysis(
                        base_mdufa_fee="19870",
                        sbd_fee_reduction="14902",
                        estimated_consulting_costs="10",
                        clinical_trial_costs="10",
                        total_estimated_cost="4968",
                    ),
                ),
                Pathway(
                    pathway="PMA",
                    costAnalysis=CostAnalysis(
                        base_mdufa_fee="75",
                        sbd_fee_reduction="14902",
                        estimated_consulting_costs="10",
                        clinical_trial_costs="10",
                        total_estimated_cost="4968",
                    ),
                ),
            ],
        )
        # Save to database
        await dummy_cost_estimation.save()
        
        # Return with product data
        return [CostEstimationResponse(
            product_id=str(product_id),
            product_name=product_name,
            product_code=product_code,
            can_apply_for_sbd=dummy_cost_estimation.can_apply_for_sbd,
            pathways=dummy_cost_estimation.pathways
        )]

    # Convert existing estimations to response format with product data
    return [
        CostEstimationResponse(
            product_id=estimation.product_id,
            product_name=product_name,
            product_code=product_code,
            can_apply_for_sbd=estimation.can_apply_for_sbd,
            pathways=estimation.pathways
        )
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
