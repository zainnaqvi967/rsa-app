"""
Authentication router with phone + OTP endpoints.

This module provides authentication endpoints for the roadside assistance marketplace.
Uses a demo OTP ("1234") for development purposes.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import User, UserRole
from backend.schemas import UserRead
from backend.utils.auth import create_access_token
from backend.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Schemas

class RequestOTPInput(BaseModel):
    """Input schema for requesting OTP."""
    phone: str = Field(..., min_length=1, description="Phone number")


class RequestOTPResponse(BaseModel):
    """Response schema for OTP request."""
    message: str
    demoOtp: str


class VerifyOTPInput(BaseModel):
    """Input schema for verifying OTP and logging in."""
    phone: str = Field(..., min_length=1, description="Phone number")
    otp: str = Field(..., description="OTP code")
    name: Optional[str] = Field(None, description="User's name (for new accounts)")


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


# Endpoints

@router.post("/request-otp", response_model=RequestOTPResponse)
def request_otp(input_data: RequestOTPInput):
    """
    Request OTP for phone number authentication.
    
    **Demo Mode:** Always returns OTP "1234". No SMS is sent.
    
    Args:
        input_data: Contains phone number
    
    Returns:
        Message confirming OTP sent with demo OTP included
    
    Example:
        ```json
        POST /auth/request-otp
        {
            "phone": "+1234567890"
        }
        
        Response:
        {
            "message": "OTP sent",
            "demoOtp": "1234"
        }
        ```
    """
    # Validate phone is not empty (basic validation)
    if not input_data.phone.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number cannot be empty"
        )
    
    # In production, this would:
    # 1. Generate a random OTP
    # 2. Store it in cache/database with expiry
    # 3. Send SMS via provider (Twilio, etc.)
    
    return RequestOTPResponse(
        message="OTP sent",
        demoOtp=settings.DEMO_OTP
    )


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(
    input_data: VerifyOTPInput,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and authenticate user.
    
    **Demo Mode:** Only accepts OTP "1234".
    
    - If user exists: Log them in
    - If user is new: Create account with customer role
    
    Args:
        input_data: Contains phone, OTP, and optional name
        db: Database session
    
    Returns:
        JWT access token and user information
    
    Raises:
        HTTPException: 400 if OTP is invalid
    
    Example:
        ```json
        POST /auth/verify-otp
        {
            "phone": "+1234567890",
            "otp": "1234",
            "name": "John Doe"
        }
        
        Response:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "name": "John Doe",
                "phone": "+1234567890",
                "role": "customer",
                "created_at": "2025-12-01T00:00:00",
                "updated_at": "2025-12-01T00:00:00"
            }
        }
        ```
    """
    # Validate OTP
    if input_data.otp != settings.DEMO_OTP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Look up or create user
    user = db.query(User).filter(User.phone == input_data.phone).first()
    
    if user is None:
        # Create new user
        # Generate default name if not provided
        default_name = f"User {input_data.phone[-4:]}" if len(input_data.phone) >= 4 else "User"
        user_name = input_data.name if input_data.name else default_name
        
        user = User(
            phone=input_data.phone,
            name=user_name,
            role=UserRole.CUSTOMER  # Default role for new users
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT token
    token_data = {
        "sub": str(user.id),  # Subject (user ID)
        "role": user.role.value,  # User role
        "phone": user.phone
    }
    access_token = create_access_token(data=token_data)
    
    # Convert user to schema
    user_schema = UserRead.model_validate(user)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_schema
    )

