"""Pydantic schemas for ServiceRequest model."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field

from backend.models.service_request import ServiceType, VehicleType, RequestStatus

if TYPE_CHECKING:
    from backend.schemas.offer import OfferRead
    from backend.schemas.job import JobRead


class ServiceRequestBase(BaseModel):
    """Base service request schema."""
    service_type: ServiceType
    vehicle_type: VehicleType
    description: Optional[str] = None
    price_offered: float = Field(..., gt=0, description="Price in currency units")
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lng: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class ServiceRequestCreate(ServiceRequestBase):
    """Schema for creating a service request."""
    pass


class ServiceRequestUpdate(BaseModel):
    """Schema for updating a service request."""
    description: Optional[str] = None
    price_offered: Optional[float] = Field(None, gt=0)
    status: Optional[RequestStatus] = None


class ServiceRequestRead(ServiceRequestBase):
    """Schema for reading service request data."""
    id: int
    customer_id: int
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceRequestWithOffers(ServiceRequestRead):
    """Schema for reading service request with offers."""
    offers: List["OfferRead"] = []

    class Config:
        from_attributes = True


class ServiceRequestWithJob(ServiceRequestRead):
    """Schema for reading service request with job details."""
    offers: List["OfferRead"] = []
    job: Optional["JobRead"] = None

    class Config:
        from_attributes = True

