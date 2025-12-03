"""
Admin API endpoints for system management and monitoring.

All endpoints require authentication with admin role.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.deps import get_current_admin
from backend.models import (
    User, UserRole, ProviderProfile, ServiceRequest, 
    Offer, Job, RequestStatus, JobStatus
)
from backend.schemas.admin_schemas import (
    UserListItem,
    ProviderListItem,
    ProviderVerificationUpdate,
    ServiceRequestListItem,
    JobListItem,
)
from backend.schemas import ProviderProfileRead


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserListItem])
def list_users(
    role: Optional[str] = Query(None, description="Filter by role (customer, provider, admin)"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all users with optional role filter.
    
    Args:
        role: Optional role filter (customer, provider, admin)
        current_admin: Authenticated admin user
        db: Database session
    
    Returns:
        List of users with basic information
    
    Example:
        ```bash
        # All users
        curl http://localhost:8000/admin/users \
          -H "Authorization: Bearer <admin-token>"
        
        # Only customers
        curl "http://localhost:8000/admin/users?role=customer" \
          -H "Authorization: Bearer <admin-token>"
        ```
    """
    query = db.query(User)
    
    # Apply role filter if provided
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: customer, provider, admin"
            )
    
    users = query.order_by(User.created_at.desc()).all()
    
    return users


@router.get("/providers", response_model=List[ProviderListItem])
def list_providers(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all provider profiles with user information.
    
    Args:
        current_admin: Authenticated admin user
        db: Database session
    
    Returns:
        List of providers with profile and user information
    
    Example:
        ```bash
        curl http://localhost:8000/admin/providers \
          -H "Authorization: Bearer <admin-token>"
        ```
    """
    # Query with join to get user info
    providers = db.query(
        ProviderProfile.id.label('provider_profile_id'),
        ProviderProfile.user_id,
        User.name.label('user_name'),
        User.phone.label('user_phone'),
        ProviderProfile.city,
        ProviderProfile.services_offered,
        ProviderProfile.vehicle_types,
        ProviderProfile.is_verified,
        ProviderProfile.is_online,
        ProviderProfile.average_rating,
        ProviderProfile.total_ratings
    ).join(User).order_by(ProviderProfile.id.desc()).all()
    
    # Convert to list of dicts for Pydantic
    result = []
    for p in providers:
        result.append(ProviderListItem(
            provider_profile_id=p.provider_profile_id,
            user_id=p.user_id,
            user_name=p.user_name,
            user_phone=p.user_phone,
            city=p.city,
            services_offered=p.services_offered,
            vehicle_types=p.vehicle_types,
            is_verified=p.is_verified,
            is_online=p.is_online,
            average_rating=p.average_rating,
            total_ratings=p.total_ratings
        ))
    
    return result


@router.patch("/providers/{provider_profile_id}", response_model=ProviderProfileRead)
def update_provider_verification(
    provider_profile_id: int,
    update_data: ProviderVerificationUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update provider verification status.
    
    Admins can verify or unverify providers.
    
    Args:
        provider_profile_id: Provider profile ID
        update_data: Verification status update
        current_admin: Authenticated admin user
        db: Database session
    
    Returns:
        Updated provider profile
    
    Raises:
        HTTPException: 404 if provider profile not found
    
    Example:
        ```json
        PATCH /admin/providers/1
        {
            "is_verified": true
        }
        ```
    """
    # Get provider profile
    profile = db.query(ProviderProfile).filter(
        ProviderProfile.id == provider_profile_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider profile not found"
        )
    
    # Update verification status
    profile.is_verified = update_data.is_verified
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/service-requests", response_model=List[ServiceRequestListItem])
def list_service_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of service requests with offer counts.
    
    Args:
        status: Optional status filter (pending_offers, offer_selected, cancelled, expired)
        customer_id: Optional customer ID filter
        current_admin: Authenticated admin user
        db: Database session
    
    Returns:
        List of service requests with offer counts
    
    Example:
        ```bash
        # All requests
        curl http://localhost:8000/admin/service-requests \
          -H "Authorization: Bearer <admin-token>"
        
        # Pending requests only
        curl "http://localhost:8000/admin/service-requests?status=pending_offers" \
          -H "Authorization: Bearer <admin-token>"
        
        # Requests for specific customer
        curl "http://localhost:8000/admin/service-requests?customer_id=5" \
          -H "Authorization: Bearer <admin-token>"
        ```
    """
    # Build query with offer count
    query = db.query(
        ServiceRequest.id,
        ServiceRequest.customer_id,
        User.name.label('customer_name'),
        ServiceRequest.service_type,
        ServiceRequest.vehicle_type,
        ServiceRequest.description,
        ServiceRequest.price_offered,
        ServiceRequest.lat,
        ServiceRequest.lng,
        ServiceRequest.status,
        ServiceRequest.created_at,
        ServiceRequest.updated_at,
        func.count(Offer.id).label('offer_count')
    ).join(
        User, ServiceRequest.customer_id == User.id
    ).outerjoin(
        Offer, ServiceRequest.id == Offer.service_request_id
    ).group_by(
        ServiceRequest.id, User.name
    )
    
    # Apply filters
    if status:
        try:
            status_enum = RequestStatus(status)
            query = query.filter(ServiceRequest.status == status_enum)
        except ValueError:
            valid_statuses = [s.value for s in RequestStatus]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
    
    if customer_id:
        query = query.filter(ServiceRequest.customer_id == customer_id)
    
    # Execute query
    requests = query.order_by(ServiceRequest.created_at.desc()).all()
    
    # Convert to response schema
    result = []
    for r in requests:
        result.append(ServiceRequestListItem(
            id=r.id,
            customer_id=r.customer_id,
            customer_name=r.customer_name,
            service_type=r.service_type.value,
            vehicle_type=r.vehicle_type.value,
            description=r.description,
            price_offered=r.price_offered,
            lat=r.lat,
            lng=r.lng,
            status=r.status.value,
            offer_count=r.offer_count,
            created_at=r.created_at,
            updated_at=r.updated_at
        ))
    
    return result


@router.get("/jobs", response_model=List[JobListItem])
def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of jobs with related information.
    
    Args:
        status: Optional job status filter (assigned, on_the_way, arrived, in_progress, completed, cancelled)
        current_admin: Authenticated admin user
        db: Database session
    
    Returns:
        List of jobs with service request and user information
    
    Example:
        ```bash
        # All jobs
        curl http://localhost:8000/admin/jobs \
          -H "Authorization: Bearer <admin-token>"
        
        # Active jobs only
        curl "http://localhost:8000/admin/jobs?status=in_progress" \
          -H "Authorization: Bearer <admin-token>"
        ```
    """
    # Build query with joins to get all related info
    query = db.query(
        Job.id.label('job_id'),
        Job.status.label('job_status'),
        Job.created_at.label('job_created_at'),
        Job.updated_at.label('job_updated_at'),
        ServiceRequest.id.label('service_request_id'),
        ServiceRequest.service_type,
        ServiceRequest.vehicle_type,
        ServiceRequest.customer_id,
        User.name.label('customer_name'),
        Offer.provider_id,
    ).join(
        ServiceRequest, Job.service_request_id == ServiceRequest.id
    ).join(
        User, ServiceRequest.customer_id == User.id
    ).join(
        Offer, Job.offer_id == Offer.id
    )
    
    # Apply status filter if provided
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(Job.status == status_enum)
        except ValueError:
            valid_statuses = [s.value for s in JobStatus]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
    
    # Execute query
    jobs_data = query.order_by(Job.created_at.desc()).all()
    
    # Get provider names in a separate query to avoid duplicate User joins
    provider_ids = [j.provider_id for j in jobs_data]
    providers = db.query(User.id, User.name).filter(User.id.in_(provider_ids)).all()
    provider_names = {p.id: p.name for p in providers}
    
    # Convert to response schema
    result = []
    for j in jobs_data:
        result.append(JobListItem(
            job_id=j.job_id,
            job_status=j.job_status.value,
            job_created_at=j.job_created_at,
            job_updated_at=j.job_updated_at,
            service_request_id=j.service_request_id,
            service_type=j.service_type.value,
            vehicle_type=j.vehicle_type.value,
            customer_id=j.customer_id,
            customer_name=j.customer_name,
            provider_id=j.provider_id,
            provider_name=provider_names.get(j.provider_id)
        ))
    
    return result

