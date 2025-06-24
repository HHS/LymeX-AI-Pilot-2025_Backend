from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, HTTPException, status

from src.modules.authentication.dependencies import get_current_user
from src.modules.authorization.dependencies import get_current_company
from src.modules.company.models import Company
from src.modules.user.models import User
from src.modules.search_bar.schema import UnifiedSearchResult
from src.modules.search_bar.service import unified_search

router = APIRouter()


@router.get("/", response_model=List[UnifiedSearchResult])
async def search_products_handler(
    query: Annotated[str, Query(..., description="Search query string")],
    current_user: Annotated[User, Depends(get_current_user)],
    current_company: Annotated[Company, Depends(get_current_company)],
) -> List[UnifiedSearchResult]:
    """
    Unified search for products and related modules within the current company.
    Returns a list of matches across multiple models.
    """
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    return await unified_search(current_company, query.strip())
