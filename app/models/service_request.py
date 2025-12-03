"""
Service Request Model
=====================
This model represents a request for roadside assistance.

For beginners:
- A customer creates a ServiceRequest when they need help
- The request includes: what's wrong, car details, location
- Providers can see pending requests and accept them
- The status tracks the lifecycle: PENDING → ACCEPTED → ON_THE_WAY → COMPLETED

Think of it like ordering food delivery:
1. You place an order (PENDING)
2. A restaurant accepts it (ACCEPTED)
3. Driver is on the way (ON_THE_WAY)
4. Food is delivered (COMPLETED)
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship

# Import Base from our database setup
from app.database import Base


# ====================
# REQUEST STATUS ENUM
# ====================
class RequestStatus(str, enum.Enum):
    """
    Possible statuses for a service request.
    
    Lifecycle:
    PENDING → ACCEPTED → ON_THE_WAY → COMPLETED
           ↘ CANCELLED (can happen at any point)
    """
    PENDING = "pending"       # Waiting for a provider to accept
    ACCEPTED = "accepted"     # Provider has accepted, preparing to go
    ON_THE_WAY = "on_the_way" # Provider is traveling to customer
    IN_PROGRESS = "in_progress"  # Provider is working on the vehicle
    COMPLETED = "completed"   # Service finished successfully
    CANCELLED = "cancelled"   # Request was cancelled


# ====================
# SERVICE REQUEST MODEL
# ====================
class ServiceRequest(Base):
    """
    Service Request table - stores all roadside assistance requests.
    
    Table name: 'service_requests'
    
    Relationships:
    - Each request belongs to ONE customer (who created it)
    - Each request can have ONE provider (who accepted it) - nullable until accepted
    """
    
    __tablename__ = "service_requests"
    
    # ====================
    # PRIMARY KEY
    # ====================
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the request"
    )
    
    # ====================
    # FOREIGN KEYS (Links to other tables)
    # ====================
    
    # Who created this request (the customer)
    # ForeignKey("users.id") links to the 'id' column of the 'users' table
    # nullable=False because every request MUST have a customer
    customer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),  # If user deleted, delete their requests
        nullable=False,
        index=True,  # Index for finding all requests by a customer
        comment="ID of the customer who created this request"
    )
    
    # Who accepted this request (the provider)
    # nullable=True because when first created, no provider has accepted yet
    provider_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),  # If provider deleted, set to NULL
        nullable=True,  # Nullable until a provider accepts
        index=True,  # Index for finding all jobs by a provider
        comment="ID of the provider who accepted this request (null until accepted)"
    )
    
    # ====================
    # REQUEST DETAILS
    # ====================
    
    # What's the problem?
    # Text allows for long descriptions (no length limit like String)
    description = Column(
        Text,
        nullable=False,
        comment="Description of the problem (e.g., 'Flat tire on highway')"
    )
    
    # ====================
    # VEHICLE INFORMATION
    # ====================
    
    vehicle_make = Column(
        String(50),
        nullable=False,
        comment="Vehicle manufacturer (e.g., Toyota, Honda, Ford)"
    )
    
    vehicle_model = Column(
        String(50),
        nullable=False,
        comment="Vehicle model (e.g., Camry, Civic, F-150)"
    )
    
    # Year can be string to handle edge cases like "2024" or "Unknown"
    vehicle_year = Column(
        String(10),
        nullable=True,
        comment="Vehicle year (e.g., '2020')"
    )
    
    # ====================
    # LOCATION INFORMATION
    # ====================
    
    # Human-readable location description
    location_text = Column(
        String(255),
        nullable=False,
        comment="Text description of location (e.g., '123 Main St' or 'Highway 101 near exit 25')"
    )
    
    # GPS coordinates for mapping (optional for now)
    # Float for decimal precision (e.g., 37.7749, -122.4194)
    latitude = Column(
        Float,
        nullable=True,
        comment="GPS latitude coordinate"
    )
    
    longitude = Column(
        Float,
        nullable=True,
        comment="GPS longitude coordinate"
    )
    
    # ====================
    # STATUS TRACKING
    # ====================
    
    status = Column(
        Enum(RequestStatus),
        nullable=False,
        default=RequestStatus.PENDING,
        index=True,  # Index for filtering by status (very common query!)
        comment="Current status of the request"
    )
    
    # ====================
    # TIMESTAMPS
    # ====================
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,  # Index for sorting by newest first
        comment="When the request was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When the request was last updated"
    )
    
    # ====================
    # RELATIONSHIPS
    # ====================
    
    # Link to the customer who created this request
    # 'back_populates' creates a two-way link
    customer = relationship(
        "User",
        back_populates="customer_requests",
        foreign_keys=[customer_id]  # Specify which FK (since there are two User FKs)
    )
    
    # Link to the provider who accepted this request
    provider = relationship(
        "User",
        back_populates="provider_jobs",
        foreign_keys=[provider_id]
    )
    
    # ====================
    # METHODS
    # ====================
    
    def __repr__(self):
        """String representation for debugging."""
        return (
            f"<ServiceRequest("
            f"id={self.id}, "
            f"status='{self.status.value}', "
            f"customer_id={self.customer_id}, "
            f"provider_id={self.provider_id}"
            f")>"
        )
    
    def is_pending(self) -> bool:
        """Check if request is waiting for a provider."""
        return self.status == RequestStatus.PENDING
    
    def is_active(self) -> bool:
        """Check if request is in progress (not completed or cancelled)."""
        return self.status in [
            RequestStatus.PENDING,
            RequestStatus.ACCEPTED,
            RequestStatus.ON_THE_WAY,
            RequestStatus.IN_PROGRESS
        ]
    
    def is_completed(self) -> bool:
        """Check if request is finished."""
        return self.status == RequestStatus.COMPLETED
    
    def can_be_accepted(self) -> bool:
        """Check if a provider can accept this request."""
        return self.status == RequestStatus.PENDING and self.provider_id is None


# ====================
# COMPOSITE INDEXES
# ====================
# These indexes speed up common queries that filter on multiple columns

# Index for finding pending requests in a location (providers searching for jobs)
Index("ix_service_requests_status_created", ServiceRequest.status, ServiceRequest.created_at)

