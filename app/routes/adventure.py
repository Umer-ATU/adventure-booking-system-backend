"""
Adventure routes for browsing and management.
"""
from typing import Optional
import math

from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.database import get_database
from app.core.deps import get_current_admin, get_optional_user
from app.repositories.adventure import AdventureRepository
from app.schemas.adventure import (
    AdventureCreate,
    AdventureUpdate,
    AdventureResponse,
    AdventureListResponse,
    AdventureCategory,
    DifficultyLevel,
)
from app.schemas.user import UserInDB

router = APIRouter(prefix="/adventures", tags=["Adventures"])


async def get_adventure_repository(
    client: AsyncIOMotorClient = Depends(get_database)
) -> AdventureRepository:
    """Get adventure repository instance."""
    database = client[settings.MONGODB_DB_NAME]
    return AdventureRepository(database)


# ============== Public Endpoints ==============

@router.get("", response_model=AdventureListResponse)
async def list_adventures(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[AdventureCategory] = Query(None, description="Filter by category"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    location: Optional[str] = Query(None, description="Filter by location"),
    is_featured: Optional[bool] = Query(None, description="Featured only"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=50, description="Items per page"),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """
    List all active adventures with search and filters.
    
    Supports:
    - Full-text search on title, description, tags
    - Filter by category, difficulty, price range, location
    - Sorting and pagination
    """
    skip = (page - 1) * page_size
    
    adventures, total = await repo.get_all(
        skip=skip,
        limit=page_size,
        query=query,
        category=category,
        difficulty=difficulty,
        min_price=min_price,
        max_price=max_price,
        location=location,
        is_active=True,
        is_featured=is_featured,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return AdventureListResponse(
        items=adventures,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/featured", response_model=list[AdventureResponse])
async def get_featured_adventures(
    limit: int = Query(6, ge=1, le=20),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """Get featured adventures for homepage."""
    return await repo.get_featured(limit=limit)


@router.get("/categories")
async def get_category_counts(
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """Get count of adventures per category."""
    counts = await repo.get_categories_count()
    return {
        "categories": [
            {"name": cat.value, "label": cat.value.replace("_", " ").title(), "count": counts.get(cat.value, 0)}
            for cat in AdventureCategory
        ]
    }


@router.get("/{adventure_id}", response_model=AdventureResponse)
async def get_adventure(
    adventure_id: str,
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """Get adventure details by ID."""
    adventure = await repo.get_by_id(adventure_id)
    
    if not adventure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adventure not found"
        )
    
    return adventure


# ============== Admin Endpoints ==============

@router.post("", response_model=AdventureResponse, status_code=status.HTTP_201_CREATED)
async def create_adventure(
    adventure_data: AdventureCreate,
    current_admin: UserInDB = Depends(get_current_admin),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """
    Create a new adventure. Admin only.
    
    Requires admin authentication.
    """
    adventure = await repo.create(adventure_data, created_by=current_admin.id)
    return adventure


@router.put("/{adventure_id}", response_model=AdventureResponse)
async def update_adventure(
    adventure_id: str,
    adventure_update: AdventureUpdate,
    current_admin: UserInDB = Depends(get_current_admin),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """
    Update an adventure. Admin only.
    """
    existing = await repo.get_by_id(adventure_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adventure not found"
        )
    
    updated = await repo.update(adventure_id, adventure_update)
    return updated


@router.delete("/{adventure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adventure(
    adventure_id: str,
    current_admin: UserInDB = Depends(get_current_admin),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """
    Delete an adventure. Admin only.
    """
    deleted = await repo.delete(adventure_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adventure not found"
        )
    return None


@router.patch("/{adventure_id}/toggle-featured", response_model=AdventureResponse)
async def toggle_featured(
    adventure_id: str,
    current_admin: UserInDB = Depends(get_current_admin),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """Toggle featured status of an adventure. Admin only."""
    adventure = await repo.get_by_id(adventure_id)
    if not adventure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adventure not found"
        )
    
    update = AdventureUpdate(is_featured=not adventure.is_featured)
    return await repo.update(adventure_id, update)


@router.patch("/{adventure_id}/toggle-active", response_model=AdventureResponse)
async def toggle_active(
    adventure_id: str,
    current_admin: UserInDB = Depends(get_current_admin),
    repo: AdventureRepository = Depends(get_adventure_repository)
):
    """Toggle active status of an adventure. Admin only."""
    adventure = await repo.get_by_id(adventure_id)
    if not adventure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adventure not found"
        )
    
    update = AdventureUpdate(is_active=not adventure.is_active)
    return await repo.update(adventure_id, update)
