import asyncio
from datetime import datetime, timezone
from src.modules.product.version_control.model import ProductVersionControl
from src.infrastructure.database import init_db
from src.modules.product.models import Product


async def test_async() -> None:
    await init_db()
    products = await Product.find_many().to_list()
    product_version_controls = [
        product_version_control
        for product in products
        for product_version_control in [
            ProductVersionControl(
                product_id=str(product.id),
                major_version=1,
                minor_version=1,
                comment="This is a test comment",
                created_at=datetime.now(timezone.utc),
                created_by="abcXYZ@gmail.com",
            ),
            ProductVersionControl(
                product_id=str(product.id),
                major_version=1,
                minor_version=2,
                comment="This is a test comment",
                created_at=datetime.now(timezone.utc),
                created_by="abcXYZ@gmail.com",
            ),
            ProductVersionControl(
                product_id=str(product.id),
                major_version=1,
                minor_version=3,
                comment="This is a test comment",
                created_at=datetime.now(timezone.utc),
                created_by="abcXYZ@gmail.com",
            ),
            ProductVersionControl(
                product_id=str(product.id),
                major_version=2,
                minor_version=1,
                comment="This is a test comment",
                created_at=datetime.now(timezone.utc),
                created_by="abcXYZ@gmail.com",
            ),
            ProductVersionControl(
                product_id=str(product.id),
                major_version=2,
                minor_version=2,
                comment="This is a test comment",
                created_at=datetime.now(timezone.utc),
                created_by="abcXYZ@gmail.com",
            ),
            ProductVersionControl(
                product_id=str(product.id),
                major_version=2,
                minor_version=3,
                comment="This is a test comment",
                created_at=datetime.now(timezone.utc),
                created_by="abcXYZ@gmail.com",
            ),
        ]
    ]
    await ProductVersionControl.insert_many(product_version_controls)


def test() -> None:
    asyncio.run(test_async())
