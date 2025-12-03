"""
Admin Router
============
Endpoints for platform administrators to monitor and manage the system.

For beginners:
- These endpoints are only accessible to users with role="admin"
- Admins can see ALL requests and users
- Admins can filter and search data

Protected by: get_current_admin dependency

Note: To create an admin user, you can either:
1. Use the special /admin/setup endpoint (one-time setup)
2. Manually update the database
3. Register normally and update the role in DB
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

# Our modules
from app.database import get_db
from app.models import User, UserRole, ServiceRequest, RequestStatus
from app.schemas import UserRead, ServiceRequestRead
from app.dependencies import get_current_admin, get_current_user
from app.utils.security import hash_password


# ====================
# CREATE ROUTER
# ====================
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ====================
# GET ALL REQUESTS
# ====================
@router.get(
    "/requests",
    response_model=List[ServiceRequestRead],
    summary="View all service requests",
    responses={
        200: {"description": "List of all requests"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not an admin"},
    }
)
def get_all_requests(
    # Optional filters
    status_filter: Optional[RequestStatus] = Query(
        None,
        alias="status",
        description="Filter by status (pending, accepted, etc.)"
    ),
    customer_id: Optional[int] = Query(
        None,
        description="Filter by customer ID"
    ),
    provider_id: Optional[int] = Query(
        None,
        description="Filter by provider ID"
    ),
    # Pagination (simple)
    skip: int = Query(0, ge=0, description="Skip N records"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    # Auth
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all service requests in the system.
    
    **Who can use this:** Admins only
    
    **What this does:**
    Returns all requests with optional filters.
    
    **Filters (all optional):**
    - `status`: Filter by request status (pending, accepted, etc.)
    - `customer_id`: Only requests from this customer
    - `provider_id`: Only requests assigned to this provider
    
    **Pagination:**
    - `skip`: Number of records to skip (for pagination)
    - `limit`: Maximum records to return (default 100, max 500)
    
    **Examples:**
    ```
    GET /admin/requests                       # All requests
    GET /admin/requests?status=pending        # Only pending
    GET /admin/requests?status=completed      # Only completed
    GET /admin/requests?customer_id=5         # Requests from customer 5
    GET /admin/requests?skip=0&limit=20       # First 20 requests
    ```
    """
    
    # Start with base query
    query = db.query(ServiceRequest)
    
    # Apply filters
    if status_filter:
        query = query.filter(ServiceRequest.status == status_filter)
    
    if customer_id:
        query = query.filter(ServiceRequest.customer_id == customer_id)
    
    if provider_id:
        query = query.filter(ServiceRequest.provider_id == provider_id)
    
    # Order by newest first
    query = query.order_by(ServiceRequest.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    requests = query.all()
    
    return requests


# ====================
# GET ALL USERS
# ====================
@router.get(
    "/users",
    response_model=List[UserRead],
    summary="View all users",
    responses={
        200: {"description": "List of all users"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not an admin"},
    }
)
def get_all_users(
    # Optional filters
    role_filter: Optional[UserRole] = Query(
        None,
        alias="role",
        description="Filter by role (customer, provider, admin)"
    ),
    # Pagination
    skip: int = Query(0, ge=0, description="Skip N records"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    # Auth
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users in the system.
    
    **Who can use this:** Admins only
    
    **What this does:**
    Returns all registered users with optional role filter.
    
    **Filters:**
    - `role`: Filter by user role (customer, provider, admin)
    
    **Examples:**
    ```
    GET /admin/users                    # All users
    GET /admin/users?role=customer      # Only customers
    GET /admin/users?role=provider      # Only providers
    GET /admin/users?role=admin         # Only admins
    ```
    """
    
    # Start with base query
    query = db.query(User)
    
    # Apply filter
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    # Order by newest first
    query = query.order_by(User.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    users = query.all()
    
    return users


# ====================
# GET SINGLE USER
# ====================
@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    summary="View a specific user",
    responses={
        200: {"description": "User details"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not an admin"},
        404: {"description": "User not found"},
    }
)
def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific user.
    
    **Who can use this:** Admins only
    
    **What this does:**
    Returns full details of any user in the system.
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


# ====================
# GET STATISTICS
# ====================
@router.get(
    "/stats",
    summary="Get platform statistics",
    responses={
        200: {"description": "Platform statistics"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not an admin"},
    }
)
def get_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get overall platform statistics.
    
    **Who can use this:** Admins only
    
    **What this returns:**
    - Total users by role
    - Total requests by status
    - Overall counts
    """
    
    # Count users by role
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
    total_providers = db.query(User).filter(User.role == UserRole.PROVIDER).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    # Count requests by status
    pending_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == RequestStatus.PENDING
    ).count()
    
    active_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status.in_([
            RequestStatus.ACCEPTED,
            RequestStatus.ON_THE_WAY,
            RequestStatus.IN_PROGRESS
        ])
    ).count()
    
    completed_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == RequestStatus.COMPLETED
    ).count()
    
    cancelled_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == RequestStatus.CANCELLED
    ).count()
    
    total_requests = db.query(ServiceRequest).count()
    
    return {
        "users": {
            "total": total_customers + total_providers + total_admins,
            "customers": total_customers,
            "providers": total_providers,
            "admins": total_admins,
        },
        "requests": {
            "total": total_requests,
            "pending": pending_requests,
            "active": active_requests,
            "completed": completed_requests,
            "cancelled": cancelled_requests,
        }
    }


# ====================
# ADMIN SETUP (One-time)
# ====================
@router.post(
    "/setup",
    response_model=UserRead,
    summary="Create first admin user (one-time setup)",
    responses={
        201: {"description": "Admin created"},
        400: {"description": "Admin already exists"},
    }
)
def setup_admin(
    db: Session = Depends(get_db)
):
    """
    Create the first admin user (one-time setup).
    
    **IMPORTANT:** This endpoint only works if NO admin exists yet!
    Once an admin is created, this endpoint will return an error.
    
    **What this does:**
    Creates a default admin user with:
    - Email: admin@rsa.com
    - Password: admin123
    
    **⚠️ Change the password immediately after setup!**
    
    **Note:** In production, you would:
    1. Disable this endpoint after setup
    2. Use environment variables for initial admin credentials
    3. Or create admin users through a secure internal process
    """
    
    # Check if any admin already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists. Use normal login."
        )
    
    # Create default admin
    admin_user = User(
        full_name="System Administrator",
        email="admin@rsa.com",
        phone=None,
        role=UserRole.ADMIN,
        password_hash=hash_password("admin123")  # Default password
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user


# ====================
# UPDATE USER ROLE (Admin can change roles)
# ====================
@router.patch(
    "/users/{user_id}/role",
    response_model=UserRead,
    summary="Change a user's role",
    responses={
        200: {"description": "Role updated"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not an admin"},
        404: {"description": "User not found"},
    }
)
def update_user_role(
    user_id: int,
    new_role: UserRole = Query(..., description="New role for the user"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Change a user's role.
    
    **Who can use this:** Admins only
    
    **What this does:**
    Updates the role of any user (customer ↔ provider ↔ admin).
    
    **Use cases:**
    - Promote a customer to provider after verification
    - Demote a provider back to customer
    - Create new admins
    
    **Example:**
    ```
    PATCH /admin/users/5/role?new_role=provider
    ```
    
    **⚠️ Be careful:** Changing roles affects what endpoints users can access!
    """
    
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Don't let admin demote themselves (safety)
    if user.id == current_admin.id and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin privileges"
        )
    
    # Update the role
    user.role = new_role
    
    db.commit()
    db.refresh(user)
    
    return user

