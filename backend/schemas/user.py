"""Pydantic schemas for User model."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

from backend.models.user import UserRole

if TYPE_CHECKING:
    from backend.schemas.provider_profile import ProviderProfileRead


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    name: Optional[str] = None
    phone: str = Field(..., min_length=10, description="Phone number for authentication")
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=10)


class UserRead(UserBase):
    """Schema for reading user data."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserReadWithProfile(UserRead):
    """Schema for reading user data with provider profile."""
    provider_profile: Optional["ProviderProfileRead"] = None

    class Config:
        from_attributes = True

