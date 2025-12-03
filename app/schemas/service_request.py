"""
Service Request Schemas (Pydantic Models)
=========================================
Schemas for roadside assistance service requests.

For beginners:
- These schemas handle data for creating, viewing, and updating service requests
- They connect with the ServiceRequest database model
- Input schemas (Create, Update) validate what users send
- Output schemas (Read) format what we send back

Schema purposes:
- Create: Customer submitting a new help request
- Read: Viewing request details (with customer/provider info)
- UpdateStatus: Provider/admin changing the request status
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

# Import enums from our models
from app.models.service_request import RequestStatus

# Import UserBasicInfo for nested user data in responses
from app.schemas.user import UserBasicInfo


# ====================
# BASE SCHEMA
# ====================
class ServiceRequestBase(BaseModel):
    """
    Base schema with common service request fields.
    
    Contains all the details about the problem and vehicle.
    Used as a parent class for Create and Read schemas.
    """
    
    # Problem description
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Describe the problem you're experiencing",
        examples=["Flat tire on the rear passenger side. Car is parked on the shoulder."]
    )
    
    # Vehicle information
    vehicle_make: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Vehicle manufacturer",
        examples=["Toyota", "Honda", "Ford"]
    )
    
    vehicle_model: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Vehicle model",
        examples=["Camry", "Civic", "F-150"]
    )
    
    vehicle_year: Optional[str] = Field(
        None,
        max_length=10,
        description="Vehicle year",
        examples=["2020", "2018"]
    )
    
    # Location information
    location_text: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Where are you? (address or description)",
        examples=["Highway 101, Exit 25, parked on right shoulder"]
    )
    
    latitude: Optional[float] = Field(
        None,
        ge=-90,  # Greater than or equal to -90
        le=90,   # Less than or equal to 90
        description="GPS latitude (-90 to 90)"
    )
    
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="GPS longitude (-180 to 180)"
    )


# ====================
# CREATE SCHEMA
# ====================
class ServiceRequestCreate(ServiceRequestBase):
    """
    Schema for creating a new service request.
    
    Used in: POST /requests
    
    Inherits all fields from ServiceRequestBase.
    Customer doesn't set status or provider - those are set automatically.
    
    Example request body:
    {
        "description": "Flat tire, need help changing it",
        "vehicle_make": "Honda",
        "vehicle_model": "Civic",
        "vehicle_year": "2019",
        "location_text": "Main St & 5th Ave, downtown",
        "latitude": 37.7749,
        "longitude": -122.4194
    }
    """
    pass  # All fields inherited from ServiceRequestBase


# ====================
# UPDATE STATUS SCHEMA
# ====================
class ServiceRequestUpdateStatus(BaseModel):
    """
    Schema for updating a request's status.
    
    Used in: 
    - PATCH /requests/{id}/status (provider updates status)
    - PATCH /admin/requests/{id}/status (admin can set any status)
    
    Only contains status field - nothing else can be changed this way.
    """
    status: RequestStatus = Field(
        ...,
        description="New status for the request"
    )
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: RequestStatus) -> RequestStatus:
        """
        Validate that status is a valid enum value.
        
        Pydantic already does this, but this shows how to add custom validation.
        You could add business rules here like "can't go from COMPLETED to PENDING".
        """
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "accepted"
            }
        }
    )


# ====================
# ACCEPT REQUEST SCHEMA
# ====================
class ServiceRequestAccept(BaseModel):
    """
    Schema for a provider accepting a request.
    
    Used in: POST /requests/{id}/accept
    
    This is empty for now, but you could add fields like:
    - estimated_arrival_minutes
    - provider_notes
    """
    pass  # Provider just needs to be authenticated, no extra data needed


# ====================
# READ SCHEMA (Response)
# ====================
class ServiceRequestRead(ServiceRequestBase):
    """
    Schema for returning service request data.
    
    Used in: GET /requests/{id}, GET /requests, etc.
    
    Includes:
    - All fields from ServiceRequestBase
    - id, status, timestamps
    - customer and provider info (if assigned)
    
    This is what the API returns when you fetch a request.
    """
    id: int = Field(..., description="Request unique ID")
    customer_id: int = Field(..., description="ID of customer who created request")
    provider_id: Optional[int] = Field(None, description="ID of provider (null if not assigned)")
    status: RequestStatus = Field(..., description="Current status of the request")
    created_at: datetime = Field(..., description="When request was created")
    updated_at: datetime = Field(..., description="When request was last updated")
    
    # Enable ORM mode to read from SQLAlchemy models
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "description": "Flat tire on rear passenger side",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": "2020",
                "location_text": "Highway 101, Exit 25",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "status": "pending",
                "customer_id": 1,
                "provider_id": None,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ====================
# DETAILED READ SCHEMA (with nested user info)
# ====================
class ServiceRequestDetail(ServiceRequestRead):
    """
    Detailed view of a service request with nested user information.
    
    Used in: GET /requests/{id} (detailed view)
    
    Same as ServiceRequestRead but includes:
    - customer: Basic info about who created the request
    - provider: Basic info about who's handling it (if assigned)
    
    This saves the frontend from making extra API calls to get user names.
    """
    customer: Optional[UserBasicInfo] = Field(
        None,
        description="Customer who created this request"
    )
    
    provider: Optional[UserBasicInfo] = Field(
        None,
        description="Provider handling this request (null if not assigned)"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "description": "Flat tire on rear passenger side",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": "2020",
                "location_text": "Highway 101, Exit 25",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "status": "accepted",
                "customer_id": 1,
                "provider_id": 2,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T11:00:00",
                "customer": {
                    "id": 1,
                    "full_name": "John Doe",
                    "email": "john@example.com"
                },
                "provider": {
                    "id": 2,
                    "full_name": "Mike Mechanic",
                    "email": "mike@example.com"
                }
            }
        }
    )


# ====================
# LIST RESPONSE (for paginated results)
# ====================
class ServiceRequestList(BaseModel):
    """
    Schema for listing multiple service requests.
    
    Used in: GET /requests (list all)
    
    Useful for pagination in the future.
    For now, just wraps a list of requests.
    """
    items: list[ServiceRequestRead] = Field(
        ...,
        description="List of service requests"
    )
    total: int = Field(
        ...,
        description="Total number of requests"
    )

