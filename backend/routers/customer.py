"""
Customer-facing API endpoints.

All endpoints require authentication with customer role.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.deps import get_current_customer
from backend.models import (
    User, ServiceRequest, Offer, Job,
    RequestStatus, OfferStatus, JobStatus
)
from backend.schemas import (
    ServiceRequestCreate,
    ServiceRequestRead,
)
from backend.schemas.responses import (
    ServiceRequestDetail,
    JobDetail,
    ProviderInfo,
    OfferWithProviderInfo
)


router = APIRouter(prefix="/customer", tags=["Customer"])


@router.post("/service-requests", response_model=ServiceRequestRead, status_code=status.HTTP_201_CREATED)
def create_service_request(
    request_data: ServiceRequestCreate,
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Create a new service request.
    
    The request will be visible to nearby providers who can send offers.
    
    Args:
        request_data: Service request details (type, location, price, etc.)
        current_customer: Authenticated customer
        db: Database session
    
    Returns:
        Created service request
    
    Example:
        ```json
        POST /customer/service-requests
        {
            "service_type": "flat_tyre",
            "vehicle_type": "car",
            "description": "Flat tire on Highway 101",
            "price_offered": 75.0,
            "lat": 37.7749,
            "lng": -122.4194
        }
        ```
    """
    # Create service request
    service_request = ServiceRequest(
        customer_id=current_customer.id,
        status=RequestStatus.PENDING_OFFERS,
        **request_data.model_dump()
    )
    
    db.add(service_request)
    db.commit()
    db.refresh(service_request)
    
    return service_request


@router.get("/service-requests/{request_id}", response_model=ServiceRequestDetail)
def get_service_request(
    request_id: int,
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get a service request with all offers and job details.
    
    Only returns requests belonging to the authenticated customer.
    
    Args:
        request_id: Service request ID
        current_customer: Authenticated customer
        db: Database session
    
    Returns:
        Service request with offers and job details
    
    Raises:
        HTTPException: 404 if request not found or doesn't belong to customer
    """
    # Query with eager loading of relationships
    service_request = db.query(ServiceRequest).options(
        joinedload(ServiceRequest.offers).joinedload(Offer.provider).joinedload(User.provider_profile),
        joinedload(ServiceRequest.job).joinedload(Job.offer).joinedload(Offer.provider).joinedload(User.provider_profile)
    ).filter(ServiceRequest.id == request_id).first()
    
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Verify ownership
    if service_request.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This request does not belong to you."
        )
    
    return service_request


@router.get("/active-request", response_model=Optional[ServiceRequestDetail])
def get_active_request(
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get the customer's most recent active service request.
    
    Returns requests with status "pending_offers" or "offer_selected".
    
    Args:
        current_customer: Authenticated customer
        db: Database session
    
    Returns:
        Most recent active service request or None
    """
    # Get most recent active request
    service_request = db.query(ServiceRequest).options(
        joinedload(ServiceRequest.offers).joinedload(Offer.provider).joinedload(User.provider_profile),
        joinedload(ServiceRequest.job).joinedload(Job.offer).joinedload(Offer.provider).joinedload(User.provider_profile)
    ).filter(
        ServiceRequest.customer_id == current_customer.id,
        ServiceRequest.status.in_([RequestStatus.PENDING_OFFERS, RequestStatus.OFFER_SELECTED])
    ).order_by(ServiceRequest.created_at.desc()).first()
    
    if not service_request:
        return None
    
    return service_request


@router.post("/offers/{offer_id}/accept", response_model=JobDetail)
def accept_offer(
    offer_id: int,
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Accept a provider's offer and create a job.
    
    This will:
    1. Accept the selected offer
    2. Reject all other offers for this request
    3. Update request status to "offer_selected"
    4. Create a new job with status "assigned"
    
    Args:
        offer_id: Offer ID to accept
        current_customer: Authenticated customer
        db: Database session
    
    Returns:
        Created job with details
    
    Raises:
        HTTPException: 
            - 404 if offer not found
            - 403 if request doesn't belong to customer
            - 400 if offer/request in invalid state
    """
    # Get offer with relationships
    offer = db.query(Offer).options(
        joinedload(Offer.service_request),
        joinedload(Offer.provider).joinedload(User.provider_profile)
    ).filter(Offer.id == offer_id).first()
    
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    service_request = offer.service_request
    
    # Verify ownership
    if service_request.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This request does not belong to you."
        )
    
    # Verify offer is pending
    if offer.status != OfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept offer with status '{offer.status}'. Offer must be pending."
        )
    
    # Verify request is pending offers
    if service_request.status != RequestStatus.PENDING_OFFERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept offer. Request status is '{service_request.status}'. Must be 'pending_offers'."
        )
    
    # Accept this offer
    offer.status = OfferStatus.ACCEPTED
    
    # Reject all other offers for this request
    other_offers = db.query(Offer).filter(
        Offer.service_request_id == service_request.id,
        Offer.id != offer_id,
        Offer.status == OfferStatus.PENDING
    ).all()
    
    for other_offer in other_offers:
        other_offer.status = OfferStatus.REJECTED
    
    # Update request status
    service_request.status = RequestStatus.OFFER_SELECTED
    
    # Create job
    job = Job(
        service_request_id=service_request.id,
        offer_id=offer.id,
        status=JobStatus.ASSIGNED
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Load relationships for response
    db.refresh(offer)
    job_with_details = db.query(Job).options(
        joinedload(Job.service_request),
        joinedload(Job.offer).joinedload(Offer.provider).joinedload(User.provider_profile)
    ).filter(Job.id == job.id).first()
    
    return job_with_details


@router.get("/jobs/{job_id}", response_model=JobDetail)
def get_job(
    job_id: int,
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get job details with provider information.
    
    Includes:
    - Job status and timestamps
    - Service request details
    - Offer details
    - Provider information (name, profile, current location)
    
    Args:
        job_id: Job ID
        current_customer: Authenticated customer
        db: Database session
    
    Returns:
        Job with complete details
    
    Raises:
        HTTPException: 404 if job not found or doesn't belong to customer
    """
    # Query with eager loading
    job = db.query(Job).options(
        joinedload(Job.service_request),
        joinedload(Job.offer).joinedload(Offer.provider).joinedload(User.provider_profile)
    ).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify ownership through service request
    if job.service_request.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This job does not belong to you."
        )
    
    return job

