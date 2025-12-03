"""Service request model for customer assistance requests."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class ServiceType(str, enum.Enum):
    """Service type enumeration."""
    FLAT_TYRE = "flat_tyre"
    JUMP_START = "jump_start"
    FUEL = "fuel"
    TOW = "tow"
    KEY_LOCK = "key_lock"
    OTHER = "other"


class VehicleType(str, enum.Enum):
    """Vehicle type enumeration."""
    CAR = "car"
    BIKE = "bike"


class RequestStatus(str, enum.Enum):
    """Service request status enumeration."""
    PENDING_OFFERS = "pending_offers"
    OFFER_SELECTED = "offer_selected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ServiceRequest(Base):
    """
    Service request created by customers needing assistance.
    
    Attributes:
        id: Primary key
        customer_id: Foreign key to User (customer)
        service_type: Type of service needed
        vehicle_type: Type of vehicle (car or bike)
        description: Additional details about the request
        price_offered: Price customer is willing to pay
        lat: Latitude of service location
        lng: Longitude of service location
        status: Current status of the request
        created_at: Request creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)
    description = Column(Text, nullable=True)
    price_offered = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING_OFFERS, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("User", back_populates="service_requests", foreign_keys=[customer_id])
    offers = relationship("Offer", back_populates="service_request", cascade="all, delete-orphan")
    job = relationship("Job", back_populates="service_request", uselist=False)

    def __repr__(self):
        return f"<ServiceRequest(id={self.id}, customer_id={self.customer_id}, type={self.service_type}, status={self.status})>"

