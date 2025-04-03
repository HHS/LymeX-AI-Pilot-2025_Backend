from typing import Optional
from uuid import uuid4
from fastapi import HTTPException, status
from passlib.context import CryptContext
from .schemas import UserCreateRequest, UserUpdatePasswordRequest, UserUpdateRequest
from .models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    password_hash = str(pwd_context.hash(password))
    return password_hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_matched = bool(pwd_context.verify(plain_password, hashed_password))
    return password_matched


async def create_user(data: UserCreateRequest) -> User:
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise ValueError("Email already registered")

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=hash_password(data.password),
        phone=data.phone,
        secret_token=uuid4().hex,
    )
    return await user.insert()


async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one(User.email == email)


# Frequently used, need to be cached. But just querying for now.
async def get_user_by_id(user_id: str) -> Optional[User]:
    return await User.get(user_id)


async def check_email_password(email: str, password: str) -> User:
    user = await User.find_one(User.email == email)
    if user and verify_password(password, user.password):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email or password")
