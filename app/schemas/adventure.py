"""
Adventure schemas for adventure management.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class DifficultyLevel(str, Enum):
    """Adventure difficulty level."""
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    EXTREME = "extreme"


class AdventureCategory(str, Enum):
    """Adventure categories."""
    ROLLERCOASTER = "rollercoaster"
    HAUNTED = "haunted"
    WATER = "water"
    OUTDOOR = "outdoor"
    ESCAPE_ROOM = "escape_room"
    VR_EXPERIENCE = "vr_experience"


class TimeSlot(BaseModel):
    """Time slot for adventure booking."""
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    capacity: int = Field(..., gt=0, description="Max participants per slot")
    available: int = Field(..., ge=0, description="Available spots")


class PricingTier(BaseModel):
    """Pricing tier for different participant types."""
    name: str = Field(..., description="Tier name (e.g., Adult, Child, Senior)")
    price: float = Field(..., ge=0, description="Price in currency")
    description: Optional[str] = None


class AdventureBase(BaseModel):
    """Base adventure schema."""
    title: str = Field(..., min_length=3, max_length=200, description="Adventure title")
    description: str = Field(..., min_length=10, description="Full description")
    short_description: Optional[str] = Field(None, max_length=300, description="Brief summary")
    
    # Media
    cover_image: Optional[str] = Field(None, description="Main cover image URL")
    images: List[str] = Field(default=[], description="Gallery images")
    video_url: Optional[str] = Field(None, description="Promo video URL")
    
    # Location & Details
    location: str = Field(..., description="Location name")
    address: Optional[str] = Field(None, description="Full address")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")
    
    # Categorization
    category: AdventureCategory = Field(..., description="Adventure category")
    difficulty: DifficultyLevel = Field(DifficultyLevel.MODERATE, description="Difficulty level")
    tags: List[str] = Field(default=[], description="Search tags")
    
    # Capacity & Pricing
    min_participants: int = Field(1, ge=1, description="Minimum participants")
    max_participants: int = Field(..., gt=0, description="Maximum participants")
    base_price: float = Field(..., ge=0, description="Base price per person")
    pricing_tiers: List[PricingTier] = Field(default=[], description="Different pricing options")
    
    # Rules & Requirements
    minimum_age: Optional[int] = Field(None, ge=0, description="Minimum age requirement")
    minimum_height_cm: Optional[int] = Field(None, description="Minimum height in cm")
    health_requirements: Optional[str] = Field(None, description="Health requirements text")
    inclusions: List[str] = Field(default=[], description="What's included")
    exclusions: List[str] = Field(default=[], description="What's not included")
    rules: List[str] = Field(default=[], description="Safety rules and guidelines")
    
    # Status
    is_active: bool = Field(True, description="Is adventure active and bookable")
    is_featured: bool = Field(False, description="Featured on homepage")


class AdventureCreate(AdventureBase):
    """Schema for creating a new adventure."""
    pass


class AdventureUpdate(BaseModel):
    """Schema for updating an adventure."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=300)
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    category: Optional[AdventureCategory] = None
    difficulty: Optional[DifficultyLevel] = None
    tags: Optional[List[str]] = None
    min_participants: Optional[int] = Field(None, ge=1)
    max_participants: Optional[int] = Field(None, gt=0)
    base_price: Optional[float] = Field(None, ge=0)
    pricing_tiers: Optional[List[PricingTier]] = None
    minimum_age: Optional[int] = Field(None, ge=0)
    minimum_height_cm: Optional[int] = None
    health_requirements: Optional[str] = None
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None
    rules: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class AdventureInDB(AdventureBase):
    """Schema for adventure stored in database."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Admin user ID who created")
    
    # Computed fields
    total_bookings: int = Field(0, description="Total bookings count")
    average_rating: float = Field(0.0, ge=0, le=5, description="Average user rating")
    review_count: int = Field(0, ge=0, description="Number of reviews")

    class Config:
        populate_by_name = True


class AdventureResponse(AdventureBase):
    """Schema for adventure API response."""
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    total_bookings: int = 0
    average_rating: float = 0.0
    review_count: int = 0

    class Config:
        populate_by_name = True
        from_attributes = True


class AdventureListResponse(BaseModel):
    """Paginated list of adventures."""
    items: List[AdventureResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdventureSearchParams(BaseModel):
    """Search parameters for adventures."""
    query: Optional[str] = None
    category: Optional[AdventureCategory] = None
    difficulty: Optional[DifficultyLevel] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    is_featured: Optional[bool] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 12
