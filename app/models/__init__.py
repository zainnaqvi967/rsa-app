"""
Models Package
==============
This file exports all database models so you can import them easily.

Usage:
    from app.models import User, ServiceRequest, UserRole, RequestStatus
    
Instead of:
    from app.models.user import User, UserRole
    from app.models.service_request import ServiceRequest, RequestStatus

For beginners:
- This file makes imports cleaner and shorter
- When you add a new model, add it here too!
"""

# Import models from their individual files
from app.models.user import User, UserRole
from app.models.service_request import ServiceRequest, RequestStatus

# This tells Python what to export when someone does "from app.models import *"
# It's good practice to be explicit about what you export
__all__ = [
    # User model and its enum
    "User",
    "UserRole",
    
    # ServiceRequest model and its enum
    "ServiceRequest",
    "RequestStatus",
]
