"""Provider profile model for service providers."""

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class ProviderProfile(Base):
    """
    Provider profile with service capabilities and location.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        city: Provider's operating city
        services_offered: Comma-separated service types
        vehicle_types: Types of vehicles serviced (car, bike, or both)
        is_verified: Verification status
        average_rating: Average customer rating
        total_ratings: Number of ratings received
        current_lat: Current latitude coordinate
        current_lng: Current longitude coordinate
        is_online: Online/available status
    """
    __tablename__ = "provider_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    city = Column(String, nullable=True)
    services_offered = Column(String, nullable=True)  # comma-separated: flat_tyre,jump_start,fuel,tow
    vehicle_types = Column(String, nullable=True)  # car, bike, or both
    is_verified = Column(Boolean, default=False, nullable=False)
    average_rating = Column(Float, default=5.0, nullable=False)
    total_ratings = Column(Integer, default=0, nullable=False)
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    is_online = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="provider_profile")

    def __repr__(self):
        return f"<ProviderProfile(id={self.id}, user_id={self.user_id}, city={self.city}, online={self.is_online})>"

