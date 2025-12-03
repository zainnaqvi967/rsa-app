"""
Customer Service Requests Router
================================
Endpoints for customers to create and manage their service requests.

For beginners:
- These endpoints are only accessible to users with role="customer"
- Customers can create new requests when they need roadside help
- Customers can view their own request history

Protected by: get_current_customer dependency
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Our modules
from app.database import get_db
from app.models import User, ServiceRequest, RequestStatus
from app.schemas import ServiceRequestCreate, ServiceRequestRead
from app.dependencies import get_current_customer


# ====================
# CREATE ROUTER
# ====================
router = APIRouter(
    prefix="/requests",
    tags=["Customer - Service Requests"]
)


# ====================
# CREATE SERVICE REQUEST
# ====================
@router.post(
    "/",
    response_model=ServiceRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service request",
    responses={
        201: {"description": "Request created successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a customer"},
    }
)
def create_service_request(
    request_data: ServiceRequestCreate,
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Create a new roadside assistance request.
    
    **Who can use this:** Customers only
    
    **What this does:**
    1. Creates a new service request with status "PENDING"
    2. Links the request to the current customer
    3. Returns the created request
    
    **Request body:**
    - `description`: What's wrong with your vehicle?
    - `vehicle_make`: Car manufacturer (Toyota, Honda, etc.)
    - `vehicle_model`: Car model (Camry, Civic, etc.)
    - `vehicle_year`: Year of the car (optional)
    - `location_text`: Where are you? (address or description)
    - `latitude/longitude`: GPS coordinates (optional)
    
    **Example:**
    ```json
    {
        "description": "Flat tire on the highway, need help changing it",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": "2020",
        "location_text": "Highway 101, Exit 25, right shoulder"
    }
    ```
    """
    
    # Create the service request object
    # Status is automatically set to PENDING
    # Provider is not assigned yet (null)
    new_request = ServiceRequest(
        customer_id=current_customer.id,  # Link to current customer
        provider_id=None,                  # No provider yet
        status=RequestStatus.PENDING,      # Start as pending
        description=request_data.description,
        vehicle_make=request_data.vehicle_make,
        vehicle_model=request_data.vehicle_model,
        vehicle_year=request_data.vehicle_year,
        location_text=request_data.location_text,
        latitude=request_data.latitude,
        longitude=request_data.longitude,
    )
    
    # Save to database
    db.add(new_request)
    db.commit()
    db.refresh(new_request)  # Get the auto-generated ID
    
    return new_request


# ====================
# GET MY REQUESTS
# ====================
@router.get(
    "/my",
    response_model=List[ServiceRequestRead],
    summary="Get my service requests",
    responses={
        200: {"description": "List of your requests"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a customer"},
    }
)
def get_my_requests(
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all service requests created by the current customer.
    
    **Who can use this:** Customers only
    
    **What this does:**
    Returns all requests you've created, newest first.
    
    **Use cases:**
    - Check status of your current request
    - View your request history
    - See which provider accepted your request
    """
    
    # Query all requests for this customer, ordered by newest first
    requests = db.query(ServiceRequest).filter(
        ServiceRequest.customer_id == current_customer.id
    ).order_by(
        ServiceRequest.created_at.desc()  # Newest first
    ).all()
    
    return requests


# ====================
# GET SINGLE REQUEST
# ====================
@router.get(
    "/{request_id}",
    response_model=ServiceRequestRead,
    summary="Get a specific request",
    responses={
        200: {"description": "Request details"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not your request"},
        404: {"description": "Request not found"},
    }
)
def get_request(
    request_id: int,
    current_customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific service request.
    
    **Who can use this:** Customers only (their own requests)
    
    **What this does:**
    Returns the full details of a request, including:
    - Current status
    - Assigned provider (if any)
    - All the details you submitted
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
    
    # Check if this request belongs to the current customer
    if service_request.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own requests"
        )
    
    return service_request

