"""
Schemas Package
===============
This file exports all Pydantic schemas for easy importing.

Usage:
    from app.schemas import UserCreate, UserRead, ServiceRequestCreate
    
Instead of:
    from app.schemas.user import UserCreate, UserRead
    from app.schemas.service_request import ServiceRequestCreate

For beginners:
- Schemas validate incoming data (what clients send us)
- Schemas format outgoing data (what we send back)
- Keep this file updated when you add new schemas!
"""

# ====================
# USER SCHEMAS
# ====================
from app.schemas.user import (
    # Base and common
    UserBase,
    UserBasicInfo,
    
    # Input schemas (requests)
    UserCreate,
    UserLogin,
    UserUpdate,
    
    # Output schemas (responses)
    UserRead,
    
    # Auth responses
    Token,
    TokenWithUser,
)

# ====================
# SERVICE REQUEST SCHEMAS
# ====================
from app.schemas.service_request import (
    # Base
    ServiceRequestBase,
    
    # Input schemas (requests)
    ServiceRequestCreate,
    ServiceRequestUpdateStatus,
    ServiceRequestAccept,
    
    # Output schemas (responses)
    ServiceRequestRead,
    ServiceRequestDetail,
    ServiceRequestList,
)

# ====================
# EXPORT LIST
# ====================
# This tells Python what to export with "from app.schemas import *"
__all__ = [
    # User schemas
    "UserBase",
    "UserBasicInfo",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserRead",
    "Token",
    "TokenWithUser",
    
    # Service Request schemas
    "ServiceRequestBase",
    "ServiceRequestCreate",
    "ServiceRequestUpdateStatus",
    "ServiceRequestAccept",
    "ServiceRequestRead",
    "ServiceRequestDetail",
    "ServiceRequestList",
]
