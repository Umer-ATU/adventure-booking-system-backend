from datetime import datetime
from typing import List, Optional, Dict, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.booking import BookingCreate, BookingUpdate, BookingInDB, BookingStatus


class BookingRepository:
    """Repository for booking database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.bookings

    async def create(
        self,
        booking: BookingCreate,
        user_id: Optional[str] = None,
        adventure_id: Optional[str] = None
    ) -> BookingInDB:
        """Create a new booking."""
        booking_dict = booking.model_dump()
        booking_dict["_id"] = str(ObjectId())
        booking_dict["status"] = BookingStatus.PENDING.value
        booking_dict["created_at"] = datetime.utcnow()
        booking_dict["updated_at"] = datetime.utcnow()
        
        # Enhanced fields
        if user_id:
            booking_dict["user_id"] = user_id
        if adventure_id:
            booking_dict["adventure_id"] = adventure_id
        
        # Payment fields
        booking_dict["payment_status"] = "PENDING"
        booking_dict["stripe_payment_id"] = None
        booking_dict["invoice_number"] = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{booking_dict['_id'][:8].upper()}"

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

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[BookingStatus] = None
    ) -> List[BookingInDB]:
        """Get bookings for a specific user."""
        query: Dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status.value
            
        cursor = self.collection.find(query) \
            .skip(skip) \
            .limit(limit) \
            .sort("created_at", -1)
        bookings = await cursor.to_list(length=limit)
        return [BookingInDB(**booking) for booking in bookings]

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BookingStatus] = None,
        adventure_id: Optional[str] = None
    ) -> tuple[List[BookingInDB], int]:
        """Get all bookings with pagination and filters."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status.value
        if adventure_id:
            query["adventure_id"] = adventure_id
            
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query) \
            .skip(skip) \
            .limit(limit) \
            .sort("created_at", -1)
        bookings = await cursor.to_list(length=limit)
        return [BookingInDB(**booking) for booking in bookings], total

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