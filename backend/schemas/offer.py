"""Pydantic schemas for Offer model."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

from backend.models.offer import OfferStatus

if TYPE_CHECKING:
    from backend.schemas.user import UserRead
    from backend.schemas.provider_profile import ProviderProfileRead


class OfferBase(BaseModel):
    """Base offer schema."""
    price: float = Field(..., gt=0, description="Offered price")
    eta_minutes: Optional[int] = Field(None, gt=0, description="Estimated time of arrival in minutes")


class OfferCreate(OfferBase):
    """Schema for creating an offer."""
    service_request_id: int


class OfferUpdate(BaseModel):
    """Schema for updating an offer."""
    price: Optional[float] = Field(None, gt=0)
    eta_minutes: Optional[int] = Field(None, gt=0)
    status: Optional[OfferStatus] = None


class OfferRead(OfferBase):
    """Schema for reading offer data."""
    id: int
    service_request_id: int
    provider_id: int
    status: OfferStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OfferWithProvider(OfferRead):
    """Schema for reading offer with provider details."""
    provider: "UserRead"

    class Config:
        from_attributes = True

