from src.modules.product.version_control.model import ProductVersionControl


async def get_product_version_control(
    product_id: str,
) -> list[ProductVersionControl]:
    version_controls = await ProductVersionControl.find(
        ProductVersionControl.product_id == product_id,
    ).to_list()
    return version_controls
