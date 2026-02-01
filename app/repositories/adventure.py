"""
Adventure repository for database operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import math

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.adventure import (
    AdventureCreate,
    AdventureUpdate,
    AdventureInDB,
    AdventureCategory,
    DifficultyLevel,
)


class AdventureRepository:
    """Repository for adventure database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.adventures

    async def create(self, adventure: AdventureCreate, created_by: str) -> AdventureInDB:
        """Create a new adventure."""
        adventure_dict = adventure.model_dump()
        adventure_dict["_id"] = str(ObjectId())
        adventure_dict["created_at"] = datetime.utcnow()
        adventure_dict["updated_at"] = datetime.utcnow()
        adventure_dict["created_by"] = created_by
        adventure_dict["total_bookings"] = 0
        adventure_dict["average_rating"] = 0.0
        adventure_dict["review_count"] = 0

        await self.collection.insert_one(adventure_dict)
        return AdventureInDB(**adventure_dict)

    async def get_by_id(self, adventure_id: str) -> Optional[AdventureInDB]:
        """Get adventure by ID."""
        if not ObjectId.is_valid(adventure_id):
            return None
        adventure = await self.collection.find_one({"_id": adventure_id})
        if adventure:
            return AdventureInDB(**adventure)
        return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 12,
        query: Optional[str] = None,
        category: Optional[AdventureCategory] = None,
        difficulty: Optional[DifficultyLevel] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        location: Optional[str] = None,
        is_active: Optional[bool] = True,
        is_featured: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[AdventureInDB], int]:
        """Get adventures with filters and pagination."""
        filter_query: Dict[str, Any] = {}
        
        if is_active is not None:
            filter_query["is_active"] = is_active
            
        if is_featured is not None:
            filter_query["is_featured"] = is_featured
            
        if category:
            filter_query["category"] = category.value
            
        if difficulty:
            filter_query["difficulty"] = difficulty.value
            
        if location:
            filter_query["location"] = {"$regex": location, "$options": "i"}
            
        if min_price is not None:
            filter_query["base_price"] = {"$gte": min_price}
            
        if max_price is not None:
            if "base_price" in filter_query:
                filter_query["base_price"]["$lte"] = max_price
            else:
                filter_query["base_price"] = {"$lte": max_price}
                
        if query:
            filter_query["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query.lower()]}},
            ]

        # Get total count
        total = await self.collection.count_documents(filter_query)

        # Sort direction
        sort_direction = -1 if sort_order == "desc" else 1
        
        # Get paginated results
        cursor = self.collection.find(filter_query) \
            .sort(sort_by, sort_direction) \
            .skip(skip) \
            .limit(limit)
            
        adventures = await cursor.to_list(length=limit)
        return [AdventureInDB(**adv) for adv in adventures], total

    async def get_featured(self, limit: int = 6) -> List[AdventureInDB]:
        """Get featured adventures."""
        cursor = self.collection.find(
            {"is_active": True, "is_featured": True}
        ).sort("created_at", -1).limit(limit)
        
        adventures = await cursor.to_list(length=limit)
        return [AdventureInDB(**adv) for adv in adventures]

    async def update(
        self,
        adventure_id: str,
        adventure_update: AdventureUpdate
    ) -> Optional[AdventureInDB]:
        """Update adventure."""
        if not ObjectId.is_valid(adventure_id):
            return None

        update_data = adventure_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(adventure_id)

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": adventure_id},
            {"$set": update_data}
        )

        return await self.get_by_id(adventure_id)

    async def delete(self, adventure_id: str) -> bool:
        """Delete adventure."""
        if not ObjectId.is_valid(adventure_id):
            return False
        result = await self.collection.delete_one({"_id": adventure_id})
        return result.deleted_count > 0

    async def increment_bookings(self, adventure_id: str) -> bool:
        """Increment total bookings count."""
        result = await self.collection.update_one(
            {"_id": adventure_id},
            {"$inc": {"total_bookings": 1}}
        )
        return result.modified_count > 0

    async def update_rating(
        self,
        adventure_id: str,
        new_rating: float,
        new_review_count: int
    ) -> bool:
        """Update adventure rating."""
        result = await self.collection.update_one(
            {"_id": adventure_id},
            {
                "$set": {
                    "average_rating": new_rating,
                    "review_count": new_review_count,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def count(self, is_active: Optional[bool] = None) -> int:
        """Count adventures."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        return await self.collection.count_documents(query)

    async def get_categories_count(self) -> Dict[str, int]:
        """Get count of adventures by category."""
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=100)
        return {item["_id"]: item["count"] for item in result}
