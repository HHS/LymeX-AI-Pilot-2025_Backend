from src.infrastructure.database import db
from pymongo.errors import PyMongoError


async def check_mongo_health() -> bool:
    try:
        # Use a lightweight operation like `ping`
        await db.command("ping")
        return True
    except PyMongoError:
        return False
