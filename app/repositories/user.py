"""
User repository for database operations.
"""
from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserRole
from app.core.security import get_password_hash


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users

    async def create(self, user: UserCreate, role: UserRole = UserRole.USER) -> UserInDB:
        """Create a new user."""
        user_dict = {
            "_id": str(ObjectId()),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "hashed_password": get_password_hash(user.password),
            "role": role.value,
            "is_active": True,
            "is_verified": False,
            "avatar_url": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await self.collection.insert_one(user_dict)
        return UserInDB(**user_dict)

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        if not ObjectId.is_valid(user_id):
            return None
        user = await self.collection.find_one({"_id": user_id})
        if user:
            return UserInDB(**user)
        return None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        user = await self.collection.find_one({"email": email.lower()})
        if user:
            return UserInDB(**user)
        return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None
    ) -> List[UserInDB]:
        """Get all users with optional role filter."""
        query = {}
        if role:
            query["role"] = role.value

        cursor = self.collection.find(query).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [UserInDB(**user) for user in users]

    async def update(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user profile."""
        if not ObjectId.is_valid(user_id):
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(user_id)

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )

        return await self.get_by_id(user_id)

    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password."""
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "hashed_password": get_password_hash(new_password),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def verify_user(self, user_id: str) -> bool:
        """Mark user as verified."""
        result = await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def deactivate(self, user_id: str) -> bool:
        """Deactivate user account."""
        result = await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def delete(self, user_id: str) -> bool:
        """Delete user (hard delete)."""
        if not ObjectId.is_valid(user_id):
            return False
        result = await self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    async def count(self, role: Optional[UserRole] = None) -> int:
        """Count users."""
        query = {}
        if role:
            query["role"] = role.value
        return await self.collection.count_documents(query)

    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        return await self.collection.count_documents({"email": email.lower()}) > 0
