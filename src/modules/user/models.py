from beanie import Document, Indexed, PydanticObjectId
from typing import Annotated
from datetime import datetime, timezone
from src.modules.company.storage import get_company_logo_url
from src.modules.company.models import CompanyMember
from src.modules.user.storage import get_user_avatar_url
from src.modules.user.schemas import UserCompany, UserResponse
from src.modules.user.utils import get_active_product_for_company


async def get_user_companies(user_id: str) -> list[UserCompany]:
    print(f"Fetching companies for user: {user_id}")
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$addFields": {"company_id_obj": {"$toObjectId": "$company_id"}}},
        {
            "$lookup": {
                "from": "company",
                "localField": "company_id_obj",
                "foreignField": "_id",
                "as": "company",
            }
        },
        {"$unwind": "$company"},
        {
            "$project": {
                "id": {"$toString": "$company._id"},
                "name": "$company.name",
                "description": "$company.description",
                "industry": "$company.industry",
                "street_address": "$company.street_address",
                "city": "$company.city",
                "state": "$company.state",
                "created_at": "$company.created_at",
                "updated_at": "$company.updated_at",
                "role": "$role",
                "status": "$status",
            }
        },
    ]
    results = await CompanyMember.aggregate(pipeline).to_list()

    user_companies = []
    for doc in results:
        # Get active product for this company
        active_product = await get_active_product_for_company(doc["id"], user_id)

        user_companies.append(
            UserCompany(
                **doc,
                logo=await get_company_logo_url(doc["id"]),
                active_product=active_product,
            )
        )

    return user_companies


class User(Document):
    email: Annotated[str, Indexed(unique=True)]
    first_name: str
    last_name: str
    password: str
    phone: str | None = None
    title: str | None = None
    secret_token: str
    enable_verify_login: bool = True
    enable_totp: bool = False
    verified_at: datetime | None = None
    policy_accepted_at: datetime | None = None
    deleted_at: datetime | None = None
    locked_until: datetime | None = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    is_system_admin: bool | None = False

    class Settings:
        name = "users"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def to_user_response(self, populate_companies=True) -> UserResponse:
        avatar_url = await get_user_avatar_url(str(self.id))
        user_companies = None
        if populate_companies:
            user_companies = await get_user_companies(str(self.id))
        return UserResponse(
            id=str(self.id),
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            avatar=avatar_url,
            phone=self.phone,
            title=self.title,
            enable_verify_login=self.enable_verify_login,
            enable_totp=self.enable_totp,
            verified_at=self.verified_at,
            policy_accepted_at=self.policy_accepted_at,
            deleted_at=self.deleted_at,
            locked_until=self.locked_until,
            created_at=self.created_at,
            updated_at=self.updated_at,
            companies=user_companies,
            is_system_admin=bool(self.is_system_admin),
        )
