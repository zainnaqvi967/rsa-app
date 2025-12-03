"""Additional schemas for provider endpoints."""

from typing import Optional
from pydantic import BaseModel, Field


class LocationUpdate(BaseModel):
    """Schema for updating provider location."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lng: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class JobStatusUpdate(BaseModel):
    """Schema for updating job status."""
    status: str = Field(..., description="New job status")


class NearbyServiceRequest(BaseModel):
    """Schema for nearby service request with distance."""
    id: int
    customer_id: int
    service_type: str
    vehicle_type: str
    description: Optional[str]
    price_offered: float
    lat: float
    lng: float
    status: str
    distance_km: float = Field(..., description="Distance from provider in kilometers")
    created_at: str
    
    class Config:
        from_attributes = True

