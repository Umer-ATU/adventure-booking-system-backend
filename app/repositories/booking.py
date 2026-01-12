from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.booking import BookingCreate, BookingUpdate, BookingInDB, BookingStatus


class BookingRepository:
    """Repository for booking database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.bookings

    async def create(self, booking: BookingCreate) -> BookingInDB:
        """Create a new booking."""
        booking_dict = booking.model_dump()
        booking_dict["_id"] = str(ObjectId())
        booking_dict["status"] = BookingStatus.PENDING.value
        booking_dict["created_at"] = datetime.utcnow()
        booking_dict["updated_at"] = datetime.utcnow()

        await self.collection.insert_one(booking_dict)
        return BookingInDB(**booking_dict)

    async def get_by_id(self, booking_id: str) -> Optional[BookingInDB]:
        """Get a booking by ID."""
        if not ObjectId.is_valid(booking_id):
            return None
        booking = await self.collection.find_one({"_id": booking_id})
        if booking:
            return BookingInDB(**booking)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BookingInDB]:
        """Get all bookings with pagination."""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
        bookings = await cursor.to_list(length=limit)
        return [BookingInDB(**booking) for booking in bookings]

    async def update(self, booking_id: str, booking_update: BookingUpdate) -> Optional[BookingInDB]:
        """Update a booking (admin only)."""
        if not ObjectId.is_valid(booking_id):
            return None

        update_data = booking_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(booking_id)

        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one(
            {"_id": booking_id},
            {"$set": update_data}
        )

        if result.modified_count == 0 and result.matched_count == 0:
            return None

        return await self.get_by_id(booking_id)

    async def delete(self, booking_id: str) -> bool:
        """Delete a booking."""
        if not ObjectId.is_valid(booking_id):
            return False
        result = await self.collection.delete_one({"_id": booking_id})
        return result.deleted_count > 0

    async def count(self) -> int:
        """Get total count of bookings."""
        return await self.collection.count_documents({})