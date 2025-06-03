from beanie import PydanticObjectId
from fastapi import HTTPException, status


def string_to_id(string: str) -> PydanticObjectId:
    try:
        return PydanticObjectId(string)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid string format for PydanticObjectId: {string}. Example format: 64b8f8c8e4b0f8c8e4b0f8c8",
        )
