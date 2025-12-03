"""
User Schemas (Pydantic Models)
==============================
Schemas define the SHAPE of data that goes in and out of the API.

For beginners:
- Schemas are NOT database tables - they're "data contracts"
- They validate input data (reject bad requests)
- They format output data (hide sensitive fields like passwords)
- Think of them as "forms" that define what fields are required

Naming convention:
- Base: Common fields shared by multiple schemas
- Create: Fields needed to CREATE a new record (input)
- Read: Fields to RETURN to the client (output)
- Update: Fields that can be MODIFIED (input)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Import the UserRole enum from our models
# We reuse it so API and database use the same values
from app.models.user import UserRole


# ====================
# BASE SCHEMA
# ====================
class UserBase(BaseModel):
    """
    Base schema with common user fields.
    
    Used as a parent class for other schemas.
    Does NOT include password (for security).
    
    Note: We don't use this directly in endpoints - it's just a building block.
    """
    full_name: str = Field(
        ...,  # '...' means required
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["John Doe"]
    )
    
    email: EmailStr = Field(
        ...,
        description="User's email address (must be valid format)",
        examples=["john@example.com"]
    )
    
    phone: Optional[str] = Field(
        None,  # None means optional with default None
        max_length=20,
        description="User's phone number (optional)",
        examples=["+1-555-123-4567"]
    )


# ====================
# CREATE SCHEMA (Registration)
# ====================
class UserCreate(UserBase):
    """
    Schema for creating a new user (registration).
    
    Used in: POST /auth/register
    
    Inherits all fields from UserBase and adds:
    - password (required for registration)
    - role (optional, defaults to customer)
    """
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="User's password (min 6 characters)",
        examples=["secretpassword123"]
    )
    
    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        description="User's role (defaults to customer)"
    )


# ====================
# LOGIN SCHEMA
# ====================
class UserLogin(BaseModel):
    """
    Schema for user login.
    
    Used in: POST /auth/login
    
    Only needs email and password - nothing else!
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["john@example.com"]
    )
    
    password: str = Field(
        ...,
        min_length=1,
        description="User's password",
        examples=["secretpassword123"]
    )


# ====================
# READ SCHEMA (Response)
# ====================
class UserRead(UserBase):
    """
    Schema for returning user data to the client.
    
    Used in: GET /users/me, GET /users/{id}, etc.
    
    Inherits from UserBase (name, email, phone) and adds:
    - id, role, timestamps
    
    NOTICE: No password_hash field! Never expose passwords in responses.
    
    The 'model_config' tells Pydantic to read data from SQLAlchemy models.
    This is called "ORM mode" - it converts database objects to JSON.
    """
    id: int = Field(..., description="User's unique ID")
    role: UserRole = Field(..., description="User's role")
    created_at: datetime = Field(..., description="When account was created")
    updated_at: datetime = Field(..., description="When account was last updated")
    
    # Pydantic v2 configuration
    # 'from_attributes=True' enables reading from SQLAlchemy model attributes
    model_config = ConfigDict(
        from_attributes=True,  # Equivalent to orm_mode=True in Pydantic v1
        json_schema_extra={
            "example": {
                "id": 1,
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-123-4567",
                "role": "customer",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ====================
# UPDATE SCHEMA
# ====================
class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    
    Used in: PUT /users/me, PATCH /users/{id}
    
    All fields are optional - only update what's provided.
    """
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="New full name"
    )
    
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="New phone number"
    )
    
    # Note: Email and password updates might need special endpoints
    # with additional verification (current password, email confirmation)


# ====================
# MINIMAL USER INFO (for embedding in other responses)
# ====================
class UserBasicInfo(BaseModel):
    """
    Minimal user info for embedding in other responses.
    
    Used when you need to show WHO did something without full details.
    Example: Show customer name on a service request.
    """
    id: int
    full_name: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# TOKEN RESPONSE
# ====================
class Token(BaseModel):
    """
    Schema for JWT token response after login.
    
    Used in: POST /auth/login response
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")


class TokenWithUser(Token):
    """
    Token response that also includes user info.
    
    Convenient so frontend doesn't need a separate request to get user data.
    """
    user: UserRead = Field(..., description="Logged in user's information")

