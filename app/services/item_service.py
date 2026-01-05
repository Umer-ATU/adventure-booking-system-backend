from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = db.app_db["items"]

    async def create(self, item_in: ItemCreate) -> dict:
        item_data = jsonable_encoder(item_in)
        new_item = await self.collection.insert_one(item_data)
        created_item = await self.collection.find_one({"_id": new_item.inserted_id})
        return self._map_item(created_item)

    async def get_all(self, limit: int = 100) -> List[dict]:
        items = []
        cursor = self.collection.find().limit(limit)
        async for item in cursor:
            items.append(self._map_item(item))
        return items

    async def get(self, id: str) -> Optional[dict]:
        try:
            oid = ObjectId(id)
        except:
            return None
        item = await self.collection.find_one({"_id": oid})
        return self._map_item(item) if item else None

    def _map_item(self, item: dict) -> dict:
        if item:
            item["id"] = str(item.pop("_id"))
        return item
