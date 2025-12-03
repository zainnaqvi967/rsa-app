"""
Dependencies
============
FastAPI dependencies are reusable pieces of logic that run before your endpoint.

For beginners:
- Dependencies are like "middleware" that run before your endpoint code
- They can read headers, connect to databases, check permissions, etc.
- Use Depends() in your endpoint function signature to use them

Common uses:
- Get database session
- Get current logged-in user from JWT token
- Check if user has required role

How the auth flow works:
1. Client sends request with header: "Authorization: Bearer <jwt_token>"
2. get_current_user dependency extracts and verifies the token
3. If valid, it returns the User object
4. If invalid, it raises HTTP 401 (Unauthorized)
5. Your endpoint receives the User and can use it
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Our modules
from app.database import get_db
from app.models import User, UserRole
from app.utils.security import decode_access_token


# ====================
# HTTP BEARER SECURITY
# ====================
# This tells FastAPI to look for "Authorization: Bearer <token>" header
# It also adds the 🔒 lock icon to endpoints in Swagger UI

security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token (without 'Bearer' prefix)"
)


# ====================
# GET CURRENT USER
# ====================
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Get the currently authenticated user from the JWT token.
    
    This is the main authentication dependency.
    
    Flow:
    1. Extract token from Authorization header
    2. Decode and verify the JWT token
    3. Get user ID from token payload
    4. Load user from database
    5. Return the User object
    
    Args:
        credentials: The bearer token from Authorization header (auto-injected)
        db: Database session (auto-injected)
    
    Returns:
        The User object for the authenticated user
    
    Raises:
        HTTPException 401: If token is missing, invalid, or user not found
    
    Usage in endpoints:
        @app.get("/profile")
        def get_profile(current_user: User = Depends(get_current_user)):
            return {"email": current_user.email}
    """
    
    # Get the token from credentials
    token = credentials.credentials
    
    # Decode and verify the token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user ID from token
    # "sub" (subject) is the standard JWT claim for user identifier
    user_id_str = payload.get("sub")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Convert to integer
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Load user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


# ====================
# ROLE-BASED DEPENDENCIES
# ====================
# These dependencies check if the user has the required role.
# They build on get_current_user and add role checking.

def get_current_customer(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user and verify they are a CUSTOMER.
    
    Use this to protect customer-only endpoints.
    
    Args:
        current_user: The authenticated user (from get_current_user)
    
    Returns:
        The User if they are a customer
    
    Raises:
        HTTPException 403: If user is not a customer
    
    Usage:
        @app.post("/requests")
        def create_request(customer: User = Depends(get_current_customer)):
            # Only customers can reach this code
            pass
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Customer role required."
        )
    return current_user


def get_current_provider(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user and verify they are a PROVIDER.
    
    Use this to protect provider-only endpoints.
    
    Args:
        current_user: The authenticated user (from get_current_user)
    
    Returns:
        The User if they are a provider
    
    Raises:
        HTTPException 403: If user is not a provider
    
    Usage:
        @app.post("/requests/{id}/accept")
        def accept_request(provider: User = Depends(get_current_provider)):
            # Only providers can reach this code
            pass
    """
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider role required."
        )
    return current_user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user and verify they are an ADMIN.
    
    Use this to protect admin-only endpoints.
    
    Args:
        current_user: The authenticated user (from get_current_user)
    
    Returns:
        The User if they are an admin
    
    Raises:
        HTTPException 403: If user is not an admin
    
    Usage:
        @app.get("/admin/users")
        def list_all_users(admin: User = Depends(get_current_admin)):
            # Only admins can reach this code
            pass
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user


# ====================
# TYPE ALIASES FOR CLEANER CODE
# ====================
# These make endpoint signatures cleaner and more readable

# Use these in your endpoint parameters:
# def endpoint(user: CurrentUser, db: DbSession):

CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentCustomer = Annotated[User, Depends(get_current_customer)]
CurrentProvider = Annotated[User, Depends(get_current_provider)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
DbSession = Annotated[Session, Depends(get_db)]

