from datetime import datetime, timezone
from src.environment import environment
from uuid import uuid4
from src.modules.user.models import User
from src.modules.user.service import hash_password


SYSTEM_ADMIN_EMAIL = "system.admin@example.com"


async def init_system_admin_user() -> None:
    password_hash = hash_password(environment.system_admin_password)
    existing_system_admin = await User.find_one(User.email == SYSTEM_ADMIN_EMAIL)
    if existing_system_admin:
        existing_system_admin.is_system_admin = True
        existing_system_admin.password = password_hash
        await existing_system_admin.save()
        return
    user = User(
        first_name="System",
        last_name="Admin",
        email=SYSTEM_ADMIN_EMAIL,
        password=password_hash,
        phone="000-000-0000",
        title="System Administrator",
        secret_token=uuid4().hex,
        enable_verify_login=False,
        enable_totp=False,
        verified_at=datetime.now(timezone.utc),
        policy_accepted_at=datetime.now(timezone.utc),
        is_system_admin=True,
    )
    created_user = await user.insert()
    print(f"System admin user created with ID: {created_user.id}")
    print("System admin user initialization complete.")
