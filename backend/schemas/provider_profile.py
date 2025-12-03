"""Pydantic schemas for ProviderProfile model."""

from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from backend.schemas.user import UserRead


class ProviderProfileBase(BaseModel):
    """Base provider profile schema."""
    city: Optional[str] = None
    services_offered: Optional[str] = Field(
        None, 
        description="Comma-separated services: flat_tyre,jump_start,fuel,tow,key_lock"
    )
    vehicle_types: Optional[str] = Field(
        None,
        description="Vehicle types serviced: car, bike, or both"
    )


class ProviderProfileCreate(ProviderProfileBase):
    """Schema for creating a provider profile."""
    user_id: int


class ProviderProfileUpdate(BaseModel):
    """Schema for updating provider profile."""
    city: Optional[str] = None
    services_offered: Optional[str] = None
    vehicle_types: Optional[str] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    is_online: Optional[bool] = None


class ProviderProfileRead(ProviderProfileBase):
    """Schema for reading provider profile data."""
    id: int
    user_id: int
    is_verified: bool
    average_rating: float
    total_ratings: int
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    is_online: bool

    class Config:
        from_attributes = True


class ProviderProfileWithUser(ProviderProfileRead):
    """Schema for reading provider profile with user data."""
    user: "UserRead"

    class Config:
        from_attributes = True

