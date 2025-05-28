import asyncio
from src.infrastructure.database import init_db
from src.celery.tasks.analyze_competitive_analysis import (
    analyze_competitive_analysis_task_async,
)
from src.modules.product.models import Product


async def test_async() -> None:
    await init_db()
    products = await Product.find_many().to_list()
    await asyncio.gather(
        *[
            analyze_competitive_analysis_task_async(str(product.id))
            for product in products
        ]
    )


def test() -> None:
    asyncio.run(test_async())
