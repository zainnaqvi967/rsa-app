"""Extended Pydantic schemas for nested API responses."""

from typing import Optional, List
from pydantic import BaseModel

from backend.schemas.user import UserRead
from backend.schemas.provider_profile import ProviderProfileRead
from backend.schemas.service_request import ServiceRequestRead
from backend.schemas.offer import OfferRead
from backend.schemas.job import JobRead


# Provider info with profile for offers/jobs
class ProviderInfo(BaseModel):
    """Provider information including profile data."""
    id: int
    name: Optional[str]
    phone: str
    provider_profile: Optional[ProviderProfileRead] = None
    
    class Config:
        from_attributes = True


# Offer with provider details
class OfferWithProviderInfo(OfferRead):
    """Offer with provider information."""
    provider: ProviderInfo
    
    class Config:
        from_attributes = True


# Service request with offers
class ServiceRequestWithOffersDetail(ServiceRequestRead):
    """Service request with all offers and provider info."""
    offers: List[OfferWithProviderInfo] = []
    
    class Config:
        from_attributes = True


# Service request with offers and job
class ServiceRequestDetail(ServiceRequestRead):
    """Complete service request with offers, job, and provider details."""
    offers: List[OfferWithProviderInfo] = []
    job: Optional["JobDetail"] = None
    
    class Config:
        from_attributes = True


# Job with full details
class JobDetail(JobRead):
    """Job with service request, offer, and provider details."""
    service_request: ServiceRequestRead
    offer: OfferWithProviderInfo
    
    class Config:
        from_attributes = True


# Update forward references
ServiceRequestDetail.model_rebuild()
JobDetail.model_rebuild()

