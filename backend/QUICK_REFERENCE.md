# 🚀 Quick Reference - Backend Models

## Import Guide

### Models (SQLAlchemy)

```python
from backend.models import (
    User, UserRole,
    ProviderProfile,
    ServiceRequest, ServiceType, VehicleType, RequestStatus,
    Offer, OfferStatus,
    Job, JobStatus
)
```

### Schemas (Pydantic)

```python
from backend.schemas import (
    # User schemas
    UserCreate, UserUpdate, UserRead, UserReadWithProfile,
    
    # Provider schemas
    ProviderProfileCreate, ProviderProfileUpdate, ProviderProfileRead,
    
    # Service request schemas
    ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestRead,
    ServiceRequestWithOffers, ServiceRequestWithJob,
    
    # Offer schemas
    OfferCreate, OfferUpdate, OfferRead, OfferWithProvider,
    
    # Job schemas
    JobCreate, JobUpdate, JobRead, JobWithDetails
)
```

### Database

```python
from backend.database import get_db, init_db, SessionLocal
from sqlalchemy.orm import Session
```

---

## Enums Reference

### UserRole
- `CUSTOMER` - Customer requesting service
- `PROVIDER` - Service provider
- `ADMIN` - Administrator

### ServiceType
- `FLAT_TYRE` - Flat tire repair
- `JUMP_START` - Battery jump start
- `FUEL` - Fuel delivery
- `TOW` - Vehicle towing
- `KEY_LOCK` - Lockout assistance
- `OTHER` - Other services

### VehicleType
- `CAR` - Automobile
- `BIKE` - Motorcycle

### RequestStatus
- `PENDING_OFFERS` - Waiting for provider offers
- `OFFER_SELECTED` - Customer selected an offer
- `CANCELLED` - Request cancelled
- `EXPIRED` - Request expired

### OfferStatus
- `PENDING` - Awaiting customer decision
- `ACCEPTED` - Customer accepted offer
- `REJECTED` - Customer rejected offer

### JobStatus
- `ASSIGNED` - Provider assigned to job
- `ON_THE_WAY` - Provider en route
- `ARRIVED` - Provider at location
- `IN_PROGRESS` - Service in progress
- `COMPLETED` - Job completed
- `CANCELLED` - Job cancelled

---

## Common Usage Patterns

### Create a Customer

```python
from backend.models import User, UserRole
from backend.database import SessionLocal

db = SessionLocal()

customer = User(
    name="John Doe",
    phone="+1234567890",
    role=UserRole.CUSTOMER
)
db.add(customer)
db.commit()
db.refresh(customer)
```

### Create a Provider with Profile

```python
from backend.models import User, UserRole, ProviderProfile

provider = User(
    name="Jane Smith",
    phone="+0987654321",
    role=UserRole.PROVIDER
)
db.add(provider)
db.commit()

profile = ProviderProfile(
    user_id=provider.id,
    city="San Francisco",
    services_offered="flat_tyre,jump_start,tow",
    vehicle_types="both",
    is_online=True,
    current_lat=37.7749,
    current_lng=-122.4194
)
db.add(profile)
db.commit()
```

### Create a Service Request

```python
from backend.models import ServiceRequest, ServiceType, VehicleType

request = ServiceRequest(
    customer_id=customer.id,
    service_type=ServiceType.FLAT_TYRE,
    vehicle_type=VehicleType.CAR,
    description="Flat tire on Highway 101",
    price_offered=75.0,
    lat=37.7849,
    lng=-122.4094
)
db.add(request)
db.commit()
```

### Provider Creates Offer

```python
from backend.models import Offer

offer = Offer(
    service_request_id=request.id,
    provider_id=provider.id,
    price=65.0,
    eta_minutes=15
)
db.add(offer)
db.commit()
```

### Accept Offer and Create Job

```python
from backend.models import Job, OfferStatus, RequestStatus, JobStatus

# Update statuses
offer.status = OfferStatus.ACCEPTED
request.status = RequestStatus.OFFER_SELECTED

# Create job
job = Job(
    service_request_id=request.id,
    offer_id=offer.id,
    status=JobStatus.ASSIGNED
)
db.add(job)
db.commit()
```

### Update Job Status

```python
# Provider updates as they progress
job.status = JobStatus.ON_THE_WAY
db.commit()

job.status = JobStatus.ARRIVED
db.commit()

job.status = JobStatus.IN_PROGRESS
db.commit()

job.status = JobStatus.COMPLETED
db.commit()
```

### Query with Relationships

```python
# Get user with all relationships
user = db.query(User).filter(User.id == 1).first()

# Access relationships
print(user.service_requests)  # List of requests
print(user.provider_profile)  # Profile if provider
print(user.offers)            # List of offers

# Get request with offers
request = db.query(ServiceRequest)\
    .filter(ServiceRequest.id == 1)\
    .first()

print(request.offers)    # All offers on this request
print(request.job)       # Associated job if accepted
print(request.customer)  # Customer who made request
```

---

## FastAPI Endpoint Example

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ServiceRequest
from backend.schemas import ServiceRequestCreate, ServiceRequestRead

router = APIRouter()

@router.post("/requests", response_model=ServiceRequestRead)
def create_request(
    request_data: ServiceRequestCreate,
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Create a new service request."""
    request = ServiceRequest(
        customer_id=customer_id,
        **request_data.dict()
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.get("/requests/{request_id}", response_model=ServiceRequestRead)
def get_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get a service request by ID."""
    return db.query(ServiceRequest)\
        .filter(ServiceRequest.id == request_id)\
        .first()
```

---

## Field Validation (Pydantic)

Schemas automatically validate:

- **Price fields:** Must be > 0
- **Latitude:** -90 to 90
- **Longitude:** -180 to 180
- **Phone:** Minimum 10 characters
- **Enums:** Must match defined values
- **Types:** Automatic type checking

Example:

```python
from backend.schemas import ServiceRequestCreate

# This will raise validation error (invalid lat)
try:
    data = ServiceRequestCreate(
        service_type=ServiceType.FLAT_TYRE,
        vehicle_type=VehicleType.CAR,
        price_offered=-10,  # ❌ Must be > 0
        lat=100,            # ❌ Out of range
        lng=-122.4
    )
except ValueError as e:
    print(e)
```

---

## Database Management

### Initialize Database

```python
from backend.database import init_db

init_db()  # Creates all tables
```

### Get Session

```python
from backend.database import SessionLocal

db = SessionLocal()
try:
    # Use db here
    pass
finally:
    db.close()
```

### Use as FastAPI Dependency

```python
from fastapi import Depends
from backend.database import get_db
from sqlalchemy.orm import Session

@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

---

## File Structure

```
backend/
├── database.py              # DB config
├── models/                  # SQLAlchemy models
│   ├── user.py
│   ├── provider_profile.py
│   ├── service_request.py
│   ├── offer.py
│   └── job.py
├── schemas/                 # Pydantic schemas
│   ├── user.py
│   ├── provider_profile.py
│   ├── service_request.py
│   ├── offer.py
│   └── job.py
└── routers/                 # API routes (coming soon)
```

---

## Testing

```bash
# Run test script
cd backend
python test_db.py

# Expected output:
# 🧪 Testing database setup...
# ✅ Database initialized
# 📝 Creating customer user...
# ✅ Customer created
# ... etc
```

---

## Next Steps

1. **Create API routers** in `backend/routers/`
2. **Add authentication** (JWT tokens)
3. **Implement geolocation search** (nearby providers)
4. **Add WebSocket** for real-time updates
5. **Build frontend pages** to consume API

**The data layer is complete and production-ready! 🎉**

