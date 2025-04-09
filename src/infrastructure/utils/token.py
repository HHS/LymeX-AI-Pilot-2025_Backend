from typing import Any
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from pydantic import BaseModel
from src.environment import environment
from src.modules.user.service import get_user_by_id
from src.modules.user.models import User
import hashlib


class TokenPayload(BaseModel):
    sub: str


def combine_secret(secret1: str, secret2: str) -> str:
    combined = f"{secret1}::{secret2}"
    combined_hash = hashlib.sha256(combined.encode()).hexdigest()
    return combined_hash


def encode_jwt(user: User, secret: str, expiration_seconds: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=expiration_seconds)
    secret = combine_secret(user.secret_token, secret)
    return str(
        jwt.encode(
            {
                "sub": str(user.id),
                "exp": expire,
                "iat": now,
                "iss": environment.application_name,
                "aud": environment.application_name,
            },
            secret,
        )
    )


async def decode_jwt(token: str, secret: str) -> User:
    try:
        payload = jwt.get_unverified_claims(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )
    parsed_payload = TokenPayload(**payload)
    user = await get_user_by_id(parsed_payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    secret = combine_secret(user.secret_token, secret)
    try:
        jwt.decode(
            token,
            secret,
            issuer=environment.application_name,
            audience=environment.application_name,
        )
        return user
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e
