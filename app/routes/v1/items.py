from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from app.schemas.item import ItemCreate, ItemResponse
from app.core.database import get_database
from app.services.item_service import ItemService

router = APIRouter()

def get_item_service(db: AsyncIOMotorClient = Depends(get_database)) -> ItemService:
    return ItemService(db)

@router.post("/", response_description="Add new item", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate = Body(...),
    service: ItemService = Depends(get_item_service)
):
    return await service.create(item)

@router.get("/", response_description="List all items", response_model=List[ItemResponse])
async def list_items(
    limit: int = 100,
    service: ItemService = Depends(get_item_service)
):
    return await service.get_all(limit=limit)

@router.get("/{id}", response_description="Get a single item", response_model=ItemResponse)
async def show_item(
    id: str,
    service: ItemService = Depends(get_item_service)
):
    item = await service.get(id)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")
