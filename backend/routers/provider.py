"""
Provider-facing API endpoints.

All endpoints require authentication with provider role.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.deps import get_current_provider
from backend.models import (
    User, ProviderProfile, ServiceRequest, Offer, Job,
    RequestStatus, OfferStatus, JobStatus
)
from backend.schemas import (
    ProviderProfileRead,
    ProviderProfileUpdate,
    OfferCreate,
    OfferRead,
)
from backend.schemas.provider_schemas import (
    LocationUpdate,
    JobStatusUpdate,
    NearbyServiceRequest,
)
from backend.schemas.responses import JobDetail
from backend.utils.location import haversine_distance


router = APIRouter(prefix="/provider", tags=["Provider"])


@router.get("/profile", response_model=ProviderProfileRead)
def get_provider_profile(
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get provider profile. Creates a minimal profile if none exists.
    
    Args:
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        Provider profile
    
    Example:
        ```bash
        curl http://localhost:8000/provider/profile \
          -H "Authorization: Bearer <token>"
        ```
    """
    # Get or create profile
    profile = db.query(ProviderProfile).filter(
        ProviderProfile.user_id == current_provider.id
    ).first()
    
    if not profile:
        # Create minimal profile
        profile = ProviderProfile(
            user_id=current_provider.id,
            city=None,
            services_offered=None,
            vehicle_types=None,
            is_online=False
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


@router.put("/profile", response_model=ProviderProfileRead)
def update_provider_profile(
    profile_data: ProviderProfileUpdate,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Update provider profile information.
    
    Creates profile if it doesn't exist.
    
    Args:
        profile_data: Updated profile fields
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        Updated provider profile
    
    Example:
        ```json
        PUT /provider/profile
        {
            "city": "San Francisco",
            "services_offered": "flat_tyre,jump_start,tow",
            "vehicle_types": "both",
            "is_online": true
        }
        ```
    """
    # Get or create profile
    profile = db.query(ProviderProfile).filter(
        ProviderProfile.user_id == current_provider.id
    ).first()
    
    if not profile:
        # Create new profile
        profile = ProviderProfile(user_id=current_provider.id)
        db.add(profile)
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.post("/location", response_model=ProviderProfileRead)
def update_location(
    location: LocationUpdate,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Update provider's current location.
    
    Args:
        location: New latitude and longitude
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        Updated provider profile
    
    Raises:
        HTTPException: 404 if profile doesn't exist
    
    Example:
        ```json
        POST /provider/location
        {
            "lat": 37.7749,
            "lng": -122.4194
        }
        ```
    """
    profile = db.query(ProviderProfile).filter(
        ProviderProfile.user_id == current_provider.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider profile not found. Please create profile first."
        )
    
    profile.current_lat = location.lat
    profile.current_lng = location.lng
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/nearby-requests", response_model=List[NearbyServiceRequest])
def get_nearby_requests(
    radius_km: float = Query(default=10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get service requests within specified radius.
    
    Only returns requests with status "pending_offers".
    
    Args:
        radius_km: Search radius in kilometers (default: 10.0)
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        List of nearby service requests with distances
    
    Raises:
        HTTPException: 400 if provider location not set
    
    Example:
        ```bash
        curl "http://localhost:8000/provider/nearby-requests?radius_km=15" \
          -H "Authorization: Bearer <token>"
        ```
    """
    # Get provider profile
    profile = db.query(ProviderProfile).filter(
        ProviderProfile.user_id == current_provider.id
    ).first()
    
    if not profile or profile.current_lat is None or profile.current_lng is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider location not set. Please update your location first using POST /provider/location"
        )
    
    # Get all pending requests
    pending_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == RequestStatus.PENDING_OFFERS
    ).all()
    
    # Calculate distances and filter by radius
    nearby_requests = []
    for request in pending_requests:
        distance = haversine_distance(
            profile.current_lat,
            profile.current_lng,
            request.lat,
            request.lng
        )
        
        if distance <= radius_km:
            # Convert to response schema
            request_dict = {
                "id": request.id,
                "customer_id": request.customer_id,
                "service_type": request.service_type.value,
                "vehicle_type": request.vehicle_type.value,
                "description": request.description,
                "price_offered": request.price_offered,
                "lat": request.lat,
                "lng": request.lng,
                "status": request.status.value,
                "distance_km": round(distance, 2),
                "created_at": request.created_at.isoformat()
            }
            nearby_requests.append(NearbyServiceRequest(**request_dict))
    
    # Sort by distance (closest first)
    nearby_requests.sort(key=lambda x: x.distance_km)
    
    return nearby_requests


@router.post("/offers", response_model=OfferRead, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer_data: OfferCreate,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Create an offer on a service request.
    
    Args:
        offer_data: Offer details (service_request_id, price, eta_minutes)
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        Created offer
    
    Raises:
        HTTPException: 
            - 404 if service request not found
            - 400 if request not accepting offers
            - 400 if provider already has pending offer
    
    Example:
        ```json
        POST /provider/offers
        {
            "service_request_id": 1,
            "price": 65.0,
            "eta_minutes": 15
        }
        ```
    """
    # Verify service request exists
    service_request = db.query(ServiceRequest).filter(
        ServiceRequest.id == offer_data.service_request_id
    ).first()
    
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Verify request is accepting offers
    if service_request.status != RequestStatus.PENDING_OFFERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service request is not accepting offers. Current status: {service_request.status.value}"
        )
    
    # Check if provider already has a pending offer on this request
    existing_offer = db.query(Offer).filter(
        Offer.service_request_id == offer_data.service_request_id,
        Offer.provider_id == current_provider.id,
        Offer.status == OfferStatus.PENDING
    ).first()
    
    if existing_offer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending offer on this request"
        )
    
    # Create offer
    offer = Offer(
        service_request_id=offer_data.service_request_id,
        provider_id=current_provider.id,
        price=offer_data.price,
        eta_minutes=offer_data.eta_minutes,
        status=OfferStatus.PENDING
    )
    
    db.add(offer)
    db.commit()
    db.refresh(offer)
    
    return offer


@router.get("/jobs/active", response_model=List[JobDetail])
def get_active_jobs(
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get all active jobs for the current provider.
    
    Returns jobs that are not completed or cancelled.
    
    Args:
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        List of active jobs with details
    
    Example:
        ```bash
        curl http://localhost:8000/provider/jobs/active \
          -H "Authorization: Bearer <token>"
        ```
    """
    # Get active jobs where provider's offer was accepted
    active_jobs = db.query(Job).options(
        joinedload(Job.service_request),
        joinedload(Job.offer).joinedload(Offer.provider).joinedload(User.provider_profile)
    ).join(Offer).filter(
        Offer.provider_id == current_provider.id,
        Job.status.notin_([JobStatus.COMPLETED, JobStatus.CANCELLED])
    ).all()
    
    return active_jobs


@router.patch("/jobs/{job_id}/status", response_model=JobDetail)
def update_job_status(
    job_id: int,
    status_update: JobStatusUpdate,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Update job status.
    
    Provider can update status to track job progress:
    - on_the_way: Provider is en route
    - arrived: Provider has arrived at location
    - in_progress: Service is being performed
    - completed: Job successfully completed
    - cancelled: Job was cancelled
    
    Args:
        job_id: Job ID
        status_update: New status
        current_provider: Authenticated provider
        db: Database session
    
    Returns:
        Updated job with details
    
    Raises:
        HTTPException:
            - 404 if job not found
            - 403 if job doesn't belong to provider
            - 400 if invalid status
    
    Example:
        ```json
        PATCH /provider/jobs/1/status
        {
            "status": "on_the_way"
        }
        ```
    """
    # Get job with relationships
    job = db.query(Job).options(
        joinedload(Job.service_request),
        joinedload(Job.offer).joinedload(Offer.provider).joinedload(User.provider_profile)
    ).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify job belongs to this provider
    if job.offer.provider_id != current_provider.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This job does not belong to you."
        )
    
    # Validate and parse status
    try:
        new_status = JobStatus(status_update.status)
    except ValueError:
        valid_statuses = [status.value for status in JobStatus]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Update status
    job.status = new_status
    job.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    
    return job

