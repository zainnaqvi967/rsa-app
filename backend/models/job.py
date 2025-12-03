"""Job model for tracking active service delivery."""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    ASSIGNED = "assigned"
    ON_THE_WAY = "on_the_way"
    ARRIVED = "arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Job(Base):
    """
    Job tracking the execution of an accepted offer.
    
    Attributes:
        id: Primary key
        service_request_id: Foreign key to ServiceRequest
        offer_id: Foreign key to Offer (accepted offer)
        status: Current job status
        created_at: Job creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), unique=True, nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), unique=True, nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.ASSIGNED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    service_request = relationship("ServiceRequest", back_populates="job")
    offer = relationship("Offer", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, request_id={self.service_request_id}, offer_id={self.offer_id}, status={self.status})>"

