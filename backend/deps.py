"""
Authentication dependencies for FastAPI route protection.

These dependencies can be used to protect routes and enforce role-based access control.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserRole
from backend.utils.auth import decode_token


# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
    
    Returns:
        User object for the authenticated user
    
    Raises:
        HTTPException: 401 if token is invalid or user not found
    
    Usage:
        @app.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    token = credentials.credentials
    
    # Decode the JWT token
    payload = decode_token(token)
    
    # Extract user ID from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_customer(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user and verify they have customer role.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object with customer role
    
    Raises:
        HTTPException: 403 if user is not a customer
    
    Usage:
        @app.get("/customer-only")
        def customer_route(user: User = Depends(get_current_customer)):
            return {"customer_id": user.id}
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Customer role required."
        )
    return current_user


def get_current_provider(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user and verify they have provider role.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object with provider role
    
    Raises:
        HTTPException: 403 if user is not a provider
    
    Usage:
        @app.get("/provider-only")
        def provider_route(user: User = Depends(get_current_provider)):
            return {"provider_id": user.id}
    """
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider role required."
        )
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user and verify they have admin role.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object with admin role
    
    Raises:
        HTTPException: 403 if user is not an admin
    
    Usage:
        @app.get("/admin-only")
        def admin_route(user: User = Depends(get_current_admin)):
            return {"admin_id": user.id}
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user


# Optional: Get current user without requiring authentication
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    This is useful for routes that have different behavior for authenticated vs anonymous users.
    
    Args:
        credentials: Optional bearer token
        db: Database session
    
    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except HTTPException:
        return None

