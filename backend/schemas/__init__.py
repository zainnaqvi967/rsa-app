"""Pydantic schemas for the Roadside Assistance Marketplace."""

from backend.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserRead,
    UserReadWithProfile,
)
from backend.schemas.provider_profile import (
    ProviderProfileBase,
    ProviderProfileCreate,
    ProviderProfileUpdate,
    ProviderProfileRead,
    ProviderProfileWithUser,
)
from backend.schemas.service_request import (
    ServiceRequestBase,
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestRead,
    ServiceRequestWithOffers,
    ServiceRequestWithJob,
)
from backend.schemas.offer import (
    OfferBase,
    OfferCreate,
    OfferUpdate,
    OfferRead,
    OfferWithProvider,
)
from backend.schemas.job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobRead,
    JobWithDetails,
)
from backend.schemas.responses import (
    ProviderInfo,
    OfferWithProviderInfo,
    ServiceRequestWithOffersDetail,
    ServiceRequestDetail,
    JobDetail,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserReadWithProfile",
    # Provider profile schemas
    "ProviderProfileBase",
    "ProviderProfileCreate",
    "ProviderProfileUpdate",
    "ProviderProfileRead",
    "ProviderProfileWithUser",
    # Service request schemas
    "ServiceRequestBase",
    "ServiceRequestCreate",
    "ServiceRequestUpdate",
    "ServiceRequestRead",
    "ServiceRequestWithOffers",
    "ServiceRequestWithJob",
    # Offer schemas
    "OfferBase",
    "OfferCreate",
    "OfferUpdate",
    "OfferRead",
    "OfferWithProvider",
    # Job schemas
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobRead",
    "JobWithDetails",
    # Response schemas
    "ProviderInfo",
    "OfferWithProviderInfo",
    "ServiceRequestWithOffersDetail",
    "ServiceRequestDetail",
    "JobDetail",
]
