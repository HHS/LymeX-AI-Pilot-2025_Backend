from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from src.modules.product.models import Product
from src.modules.company.models import Company, CompanyMember
from src.modules.totp.models import UserTotp
from src.modules.user.models import User
from src.modules.email.models import EmailTemplate
from src.environment import environment

client = AsyncIOMotorClient(environment.mongo_uri)
db = client[environment.mongo_db]


async def init_db() -> None:
    await init_beanie(
        database=db,
        document_models=[
            User,
            EmailTemplate,
            UserTotp,
            Company,
            CompanyMember,
            Product,
        ],
    )
