"""Admin-specific schemas for system management."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserListItem(BaseModel):
    """User list item for admin view."""
    id: int
    name: Optional[str]
    phone: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProviderListItem(BaseModel):
    """Provider with profile for admin view."""
    provider_profile_id: int
    user_id: int
    user_name: Optional[str]
    user_phone: str
    city: Optional[str]
    services_offered: Optional[str]
    vehicle_types: Optional[str]
    is_verified: bool
    is_online: bool
    average_rating: float
    total_ratings: int
    
    class Config:
        from_attributes = True


class ProviderVerificationUpdate(BaseModel):
    """Schema for updating provider verification status."""
    is_verified: bool


class ServiceRequestListItem(BaseModel):
    """Service request with offer count for admin view."""
    id: int
    customer_id: int
    customer_name: Optional[str]
    service_type: str
    vehicle_type: str
    description: Optional[str]
    price_offered: float
    lat: float
    lng: float
    status: str
    offer_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    """Job with related info for admin view."""
    job_id: int
    job_status: str
    job_created_at: datetime
    job_updated_at: datetime
    service_request_id: int
    service_type: str
    vehicle_type: str
    customer_id: int
    customer_name: Optional[str]
    provider_id: int
    provider_name: Optional[str]
    
    class Config:
        from_attributes = True

