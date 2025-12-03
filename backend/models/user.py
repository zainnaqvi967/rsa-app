"""User model for authentication and role management."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"


class User(Base):
    """
    User model representing customers, providers, and admins.
    
    Attributes:
        id: Primary key
        name: User's full name (optional)
        phone: Phone number (unique identifier for auth)
        role: User role (customer, provider, or admin)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    provider_profile = relationship("ProviderProfile", back_populates="user", uselist=False)
    service_requests = relationship("ServiceRequest", back_populates="customer", foreign_keys="ServiceRequest.customer_id")
    offers = relationship("Offer", back_populates="provider", foreign_keys="Offer.provider_id")

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, role={self.role})>"

