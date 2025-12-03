"""
Provider Router
===============
Endpoints for service providers (mechanics, tow trucks, etc.)

For beginners:
- These endpoints are only accessible to users with role="provider"
- Providers can view open requests, accept them, and update status
- The flow: View open → Accept → On the way → Arrived → In Progress → Completed

Protected by: get_current_provider dependency
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Our modules
from app.database import get_db
from app.models import User, ServiceRequest, RequestStatus
from app.schemas import ServiceRequestRead, ServiceRequestUpdateStatus
from app.dependencies import get_current_provider


# ====================
# CREATE ROUTER
# ====================
router = APIRouter(
    prefix="/provider",
    tags=["Provider"]
)


# ====================
# GET OPEN REQUESTS
# ====================
@router.get(
    "/requests/open",
    response_model=List[ServiceRequestRead],
    summary="View all open requests",
    responses={
        200: {"description": "List of open requests"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a provider"},
    }
)
def get_open_requests(
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get all service requests that are waiting for a provider.
    
    **Who can use this:** Providers only
    
    **What this does:**
    Returns all requests with status="PENDING" that haven't been
    accepted by any provider yet.
    
    **Future improvement:** Filter by location/distance
    
    **Tip:** Check this endpoint regularly to find new jobs!
    """
    
    # Query all PENDING requests (no provider assigned yet)
    open_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == RequestStatus.PENDING,
        ServiceRequest.provider_id == None  # Not assigned to anyone
    ).order_by(
        ServiceRequest.created_at.desc()  # Newest first
    ).all()
    
    return open_requests


# ====================
# GET MY JOBS
# ====================
@router.get(
    "/requests/my",
    response_model=List[ServiceRequestRead],
    summary="View my accepted jobs",
    responses={
        200: {"description": "List of your jobs"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a provider"},
    }
)
def get_my_jobs(
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get all service requests that this provider has accepted.
    
    **Who can use this:** Providers only
    
    **What this does:**
    Returns all requests assigned to you, regardless of status.
    This includes active jobs and completed ones.
    
    **Use cases:**
    - See your current active job
    - View your job history
    - Track completed jobs
    """
    
    # Query all requests assigned to this provider
    my_jobs = db.query(ServiceRequest).filter(
        ServiceRequest.provider_id == current_provider.id
    ).order_by(
        ServiceRequest.updated_at.desc()  # Most recently updated first
    ).all()
    
    return my_jobs


# ====================
# ACCEPT REQUEST
# ====================
@router.post(
    "/requests/{request_id}/accept",
    response_model=ServiceRequestRead,
    summary="Accept a service request",
    responses={
        200: {"description": "Request accepted successfully"},
        400: {"description": "Request already taken or not available"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a provider"},
        404: {"description": "Request not found"},
    }
)
def accept_request(
    request_id: int,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Accept a pending service request.
    
    **Who can use this:** Providers only
    
    **What this does:**
    1. Checks if the request is still PENDING
    2. Assigns you as the provider
    3. Changes status to ACCEPTED
    
    **Important:**
    - Only PENDING requests can be accepted
    - Once accepted, no other provider can take it
    - You're now responsible for completing this job!
    
    **After accepting:**
    Use PATCH /provider/requests/{id}/status to update the job status
    as you progress: ON_THE_WAY → ARRIVED → IN_PROGRESS → COMPLETED
    """
    
    # Find the request
    service_request = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id
    ).first()
    
    # Check if request exists
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )
    
    # Check if request is still PENDING
    if service_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request is no longer available. Current status: {service_request.status.value}"
        )
    
    # Check if already assigned to a provider
    if service_request.provider_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has already been accepted by another provider"
        )
    
    # Accept the request!
    service_request.provider_id = current_provider.id
    service_request.status = RequestStatus.ACCEPTED
    
    # Save changes
    db.commit()
    db.refresh(service_request)
    
    return service_request


# ====================
# UPDATE STATUS
# ====================
@router.patch(
    "/requests/{request_id}/status",
    response_model=ServiceRequestRead,
    summary="Update job status",
    responses={
        200: {"description": "Status updated successfully"},
        400: {"description": "Invalid status transition"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not your job or not a provider"},
        404: {"description": "Request not found"},
    }
)
def update_request_status(
    request_id: int,
    status_update: ServiceRequestUpdateStatus,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Update the status of an accepted service request.
    
    **Who can use this:** Providers only (their own jobs)
    
    **What this does:**
    Allows you to update the status as you progress through the job.
    
    **Typical status flow:**
    ```
    PENDING → ACCEPTED → ON_THE_WAY → ARRIVED → IN_PROGRESS → COMPLETED
    ```
    
    **Available statuses:**
    - `accepted` - You've accepted, preparing to go
    - `on_the_way` - You're driving to the customer
    - `arrived` - You've arrived at the location
    - `in_progress` - You're working on the vehicle
    - `completed` - Job done! 🎉
    - `cancelled` - Job was cancelled
    
    **Example:**
    ```json
    PATCH /provider/requests/1/status
    {
        "status": "on_the_way"
    }
    ```
    """
    
    # Find the request
    service_request = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id
    ).first()
    
    # Check if request exists
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )
    
    # Check if this provider owns this request
    if service_request.provider_id != current_provider.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update status for your own accepted requests"
        )
    
    # Get the new status
    new_status = status_update.status
    
    # Optional: Add business logic for valid status transitions
    # For now, we'll allow any status change except going back to PENDING
    if new_status == RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status back to PENDING"
        )
    
    # Update the status
    service_request.status = new_status
    
    # Save changes
    db.commit()
    db.refresh(service_request)
    
    return service_request


# ====================
# GET SINGLE JOB DETAIL
# ====================
@router.get(
    "/requests/{request_id}",
    response_model=ServiceRequestRead,
    summary="Get details of a job",
    responses={
        200: {"description": "Job details"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not your job"},
        404: {"description": "Request not found"},
    }
)
def get_job_detail(
    request_id: int,
    current_provider: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific job you've accepted.
    
    **Who can use this:** Providers only
    
    **What this does:**
    Returns full details of a request you've accepted, including:
    - Customer's problem description
    - Vehicle details
    - Location
    - Current status
    """
    
    # Find the request
    service_request = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id
    ).first()
    
    # Check if request exists
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )
    
    # Check if this provider owns this request
    if service_request.provider_id != current_provider.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view details for your own accepted requests"
        )
    
    return service_request

