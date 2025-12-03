"""Pydantic schemas for Job model."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel

from backend.models.job import JobStatus

if TYPE_CHECKING:
    from backend.schemas.service_request import ServiceRequestRead
    from backend.schemas.offer import OfferWithProvider


class JobBase(BaseModel):
    """Base job schema."""
    status: JobStatus


class JobCreate(BaseModel):
    """Schema for creating a job."""
    service_request_id: int
    offer_id: int


class JobUpdate(BaseModel):
    """Schema for updating job status."""
    status: JobStatus


class JobRead(JobBase):
    """Schema for reading job data."""
    id: int
    service_request_id: int
    offer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobWithDetails(JobRead):
    """Schema for reading job with full details."""
    service_request: "ServiceRequestRead"
    offer: "OfferWithProvider"

    class Config:
        from_attributes = True

