"""Offer model for provider bids on service requests."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class OfferStatus(str, enum.Enum):
    """Offer status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Offer(Base):
    """
    Offer submitted by providers for service requests.
    
    Attributes:
        id: Primary key
        service_request_id: Foreign key to ServiceRequest
        provider_id: Foreign key to User (provider)
        price: Provider's quoted price
        eta_minutes: Estimated time of arrival in minutes
        status: Current status of the offer
        created_at: Offer creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    eta_minutes = Column(Integer, nullable=True)
    status = Column(SQLEnum(OfferStatus), default=OfferStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    service_request = relationship("ServiceRequest", back_populates="offers")
    provider = relationship("User", back_populates="offers", foreign_keys=[provider_id])
    job = relationship("Job", back_populates="offer", uselist=False)

    def __repr__(self):
        return f"<Offer(id={self.id}, request_id={self.service_request_id}, provider_id={self.provider_id}, status={self.status})>"

