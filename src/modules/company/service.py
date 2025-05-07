from datetime import datetime, timezone
from beanie.operators import In
from bson import ObjectId
from fastapi import HTTPException
from src.modules.user.storage import get_user_avatar_url
from src.environment import environment
from src.celery.tasks.send_email import send_email_task
from src.modules.authorization.roles import CompanyMemberStatus, CompanyRoles
from src.modules.company.schema import CompanyMemberResponse, CreateCompanyRequest
from src.modules.company.models import Company, CompanyMember
from src.modules.user.models import User


async def get_companies(user: User, status: CompanyMemberStatus) -> list[Company]:
    company_members = await CompanyMember.find(
        CompanyMember.user_id == str(user.id),
        CompanyMember.status == status,
    ).to_list()
    company_ids = [
        ObjectId(company_member.company_id) for company_member in company_members
    ]
    companies = await Company.find(
        In(Company.id, company_ids),
    ).to_list()
    return companies


async def create_invitation(
    user: User,
    company: Company,
) -> None:
    user_already_in_company = await CompanyMember.find_one(
        CompanyMember.user_id == str(user.id),
        CompanyMember.company_id == str(company.id),
    )
    if user_already_in_company:
        raise HTTPException(
            status_code=400,
            detail="User already in company, please check your company members, invitation, or inactivated members.",
        )
    company_member = CompanyMember(
        status=CompanyMemberStatus.INVITED,
        role=CompanyRoles.USER,
        company_id=str(company.id),
        user_id=str(user.id),
        created_at=datetime.now(timezone.utc),
    )
    await company_member.insert()
    send_email_task.delay(
        "company_invitation",
        {
            "company_name": company.name,
            "invitation_link": f"{environment.frontend_url}/company/invitation/{company.id}",
        },
        user.email,
    )


async def accept_invitation(
    user: User,
    company: Company,
) -> None:
    company_member = await CompanyMember.find_one(
        CompanyMember.user_id == str(user.id),
        CompanyMember.company_id == str(company.id),
        CompanyMember.status == CompanyMemberStatus.INVITED,
    )
    if not company_member:
        raise HTTPException(
            status_code=400,
            detail="User is not invited to this company.",
        )
    company_member.status = CompanyMemberStatus.ACTIVE
    await company_member.save()


async def create_company(payload: CreateCompanyRequest) -> Company:
    created_company = Company(
        name=payload.name,
        description=payload.description,
        industry=payload.industry,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await created_company.insert()
    if payload.admin_user_id:
        admin_user = await User.get(payload.admin_user_id)
    if admin_user:
        company_member = CompanyMember(
            status=CompanyMemberStatus.ACTIVE,
            role=CompanyRoles.ADMINISTRATOR,
            company_id=str(created_company.id),
            user_id=str(admin_user.id),
            created_at=datetime.now(timezone.utc),
        )
        await company_member.insert()
    return created_company


async def get_company_members(company: Company) -> list[CompanyMemberResponse]:
    pipeline = [
        # Match the company members by company_id
        {"$match": {"company_id": str(company.id)}},
        # If company_member.user_id is stored as a string but User._id is an ObjectId,
        # convert user_id to ObjectId. Remove this stage if they already match.
        {"$addFields": {"user_obj_id": {"$toObjectId": "$user_id"}}},
        # Use $lookup to join with the users collection
        {
            "$lookup": {
                "from": "users",  # Name of the users collection
                "localField": "user_obj_id",  # Field from CompanyMember (converted to ObjectId)
                "foreignField": "_id",  # Field from User document
                "as": "user_data",  # Output array field
            }
        },
        # Unwind the joined user_data array
        {"$unwind": "$user_data"},
        # Project only the necessary fields
        {
            "$project": {
                "user_data._id": 1,
                "status": 1,
                "role": 1,
                "created_at": 1,
                "user_data.email": 1,
                "user_data.first_name": 1,
                "user_data.last_name": 1,
                "user_data.phone": 1,
            }
        },
    ]

    # Execute the aggregation pipeline
    results = await CompanyMember.aggregate(pipeline).to_list()

    # Transform the results into CompanyMemberResponse objects
    responses = []
    for doc in results:
        user_id = str(doc["user_data"]["_id"])
        responses.append(
            CompanyMemberResponse(
                user_id=user_id,
                avatar=await get_user_avatar_url(user_id),
                status=doc["status"],
                role=doc["role"],
                email=doc["user_data"]["email"],
                added_at=doc["created_at"],
                first_name=doc["user_data"]["first_name"],
                last_name=doc["user_data"]["last_name"],
                phone=doc["user_data"].get("phone"),
            )
        )

    return responses


async def deactivate_member(
    company: Company,
    user: User,
) -> None:
    company_member = await CompanyMember.find_one(
        CompanyMember.user_id == str(user.id),
        CompanyMember.company_id == str(company.id),
    )
    if not company_member:
        raise HTTPException(
            status_code=400,
            detail="User is not a member of this company.",
        )
    company_member.status = CompanyMemberStatus.INACTIVE
    await company_member.save()


async def recover_member(
    company: Company,
    user: User,
) -> None:
    company_member = await CompanyMember.find_one(
        CompanyMember.user_id == str(user.id),
        CompanyMember.company_id == str(company.id),
        CompanyMember.status == CompanyMemberStatus.INACTIVE,
    )
    if not company_member:
        raise HTTPException(
            status_code=400,
            detail="User is not a deactivated member.",
        )
    company_member.status = CompanyMemberStatus.ACTIVE
    await company_member.save()


async def update_company_member_role(
    company: Company,
    user: User,
    role: CompanyRoles,
) -> None:
    company_member = await CompanyMember.find_one(
        CompanyMember.user_id == str(user.id),
        CompanyMember.company_id == str(company.id),
        CompanyMember.status == CompanyMemberStatus.ACTIVE,
    )
    if not company_member:
        raise HTTPException(
            status_code=400,
            detail="User is not a member of this company or deactivated.",
        )
    company_member.role = role
    await company_member.save()


async def get_company_administrators(company: Company) -> list[User]:
    company_members = await CompanyMember.find(
        CompanyMember.company_id == str(company.id),
        CompanyMember.role == CompanyRoles.ADMINISTRATOR,
        CompanyMember.status == CompanyMemberStatus.ACTIVE,
    ).to_list()
    company_admins = await User.find(
        In(
            User.id,
            [ObjectId(company_member.user_id) for company_member in company_members],
        ),
    ).to_list()
    return company_admins
