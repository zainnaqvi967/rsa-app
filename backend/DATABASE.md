# 📊 Database Models Documentation

## Overview

This document describes the data model for the Roadside Assistance Marketplace MVP. The database uses SQLite with SQLAlchemy ORM.

## Entity Relationship Diagram

```
User (1) ──┬─── (0..1) ProviderProfile
           │
           ├─── (0..*) ServiceRequest (as customer)
           │              │
           │              ├─── (0..*) Offer
           │              │              │
           │              └─── (0..1) Job ─┘
           │
           └─── (0..*) Offer (as provider)
```

## Models

### 1. User

Core user model for authentication and role management.

**Table:** `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Primary key |
| name | String | Nullable | User's full name |
| phone | String | NOT NULL, UNIQUE | Phone number (used for auth) |
| role | Enum | NOT NULL | Role: customer, provider, or admin |
| created_at | DateTime | NOT NULL, Default: now() | Account creation timestamp |
| updated_at | DateTime | NOT NULL, Auto-update | Last update timestamp |

**Relationships:**
- `provider_profile` → One ProviderProfile (if role is provider)
- `service_requests` → Many ServiceRequest (as customer)
- `offers` → Many Offer (as provider)

**Enums:**
- `UserRole`: `customer`, `provider`, `admin`

---

### 2. ProviderProfile

Extended profile for service providers with capabilities and location.

**Table:** `provider_profiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Primary key |
| user_id | Integer | FK → users.id, UNIQUE | Reference to User |
| city | String | Nullable | Operating city |
| services_offered | String | Nullable | Comma-separated service types |
| vehicle_types | String | Nullable | "car", "bike", or "both" |
| is_verified | Boolean | Default: False | Verification status |
| average_rating | Float | Default: 5.0 | Average customer rating |
| total_ratings | Integer | Default: 0 | Total number of ratings |
| current_lat | Float | Nullable | Current latitude |
| current_lng | Float | Nullable | Current longitude |
| is_online | Boolean | Default: False | Online/available status |

**Relationships:**
- `user` → One User (provider)

**Service Types:**
- `flat_tyre` - Flat tire repair/replacement
- `jump_start` - Battery jump start
- `fuel` - Fuel delivery
- `tow` - Vehicle towing
- `key_lock` - Lockout assistance
- `other` - Other services

---

### 3. ServiceRequest

Customer requests for roadside assistance.

**Table:** `service_requests`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Primary key |
| customer_id | Integer | FK → users.id | Customer making the request |
| service_type | Enum | NOT NULL | Type of service needed |
| vehicle_type | Enum | NOT NULL | Vehicle type (car/bike) |
| description | Text | Nullable | Additional details |
| price_offered | Float | NOT NULL | Customer's offered price |
| lat | Float | NOT NULL | Service location latitude |
| lng | Float | NOT NULL | Service location longitude |
| status | Enum | Default: pending_offers | Request status |
| created_at | DateTime | Default: now() | Creation timestamp |
| updated_at | DateTime | Auto-update | Last update timestamp |

**Relationships:**
- `customer` → One User
- `offers` → Many Offer
- `job` → One Job (when accepted)

**Enums:**
- `ServiceType`: `flat_tyre`, `jump_start`, `fuel`, `tow`, `key_lock`, `other`
- `VehicleType`: `car`, `bike`
- `RequestStatus`: `pending_offers`, `offer_selected`, `cancelled`, `expired`

---

### 4. Offer

Provider bids/offers on service requests.

**Table:** `offers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Primary key |
| service_request_id | Integer | FK → service_requests.id | Related request |
| provider_id | Integer | FK → users.id | Provider making offer |
| price | Float | NOT NULL | Offered price |
| eta_minutes | Integer | Nullable | Estimated arrival time |
| status | Enum | Default: pending | Offer status |
| created_at | DateTime | Default: now() | Creation timestamp |
| updated_at | DateTime | Auto-update | Last update timestamp |

**Relationships:**
- `service_request` → One ServiceRequest
- `provider` → One User (provider)
- `job` → One Job (if accepted)

**Enums:**
- `OfferStatus`: `pending`, `accepted`, `rejected`

---

### 5. Job

Active job tracking after offer acceptance.

**Table:** `jobs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Primary key |
| service_request_id | Integer | FK → service_requests.id, UNIQUE | Related request |
| offer_id | Integer | FK → offers.id, UNIQUE | Accepted offer |
| status | Enum | Default: assigned | Job status |
| created_at | DateTime | Default: now() | Creation timestamp |
| updated_at | DateTime | Auto-update | Last update timestamp |

**Relationships:**
- `service_request` → One ServiceRequest
- `offer` → One Offer

**Enums:**
- `JobStatus`: `assigned`, `on_the_way`, `arrived`, `in_progress`, `completed`, `cancelled`

---

## Pydantic Schemas

Each model has corresponding Pydantic schemas for API validation:

### Schema Types

1. **Base** - Common fields shared across operations
2. **Create** - Fields required for creation
3. **Update** - Fields allowed for updates (all optional)
4. **Read** - Full model data for responses

### Nested Schemas

Some schemas include nested relationships:

- `UserReadWithProfile` - User with ProviderProfile
- `ProviderProfileWithUser` - ProviderProfile with User
- `ServiceRequestWithOffers` - ServiceRequest with Offers list
- `ServiceRequestWithJob` - ServiceRequest with Offers and Job
- `OfferWithProvider` - Offer with Provider details
- `JobWithDetails` - Job with ServiceRequest and Offer

---

## Database Setup

### Initialize Database

```python
from backend.database import init_db

# Creates all tables
init_db()
```

### Get Database Session

```python
from backend.database import get_db

# Use as dependency in FastAPI
@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

---

## Example Workflows

### 1. Customer Creates Request

```python
# Customer creates account
customer = User(name="John", phone="+123", role=UserRole.CUSTOMER)

# Customer creates service request
request = ServiceRequest(
    customer_id=customer.id,
    service_type=ServiceType.FLAT_TYRE,
    vehicle_type=VehicleType.CAR,
    price_offered=75.0,
    lat=37.7749,
    lng=-122.4194
)
```

### 2. Provider Sends Offer

```python
# Provider creates offer
offer = Offer(
    service_request_id=request.id,
    provider_id=provider.id,
    price=65.0,
    eta_minutes=15
)
```

### 3. Customer Accepts Offer

```python
# Update offer and request status
offer.status = OfferStatus.ACCEPTED
request.status = RequestStatus.OFFER_SELECTED

# Create job
job = Job(
    service_request_id=request.id,
    offer_id=offer.id,
    status=JobStatus.ASSIGNED
)
```

### 4. Provider Updates Job

```python
# Provider updates job status throughout service
job.status = JobStatus.ON_THE_WAY
job.status = JobStatus.ARRIVED
job.status = JobStatus.IN_PROGRESS
job.status = JobStatus.COMPLETED
```

---

## Testing

Run the test script to verify database setup:

```bash
cd backend
python test_db.py
```

This will:
1. Initialize the database
2. Create sample users (customer and provider)
3. Create a service request
4. Create an offer
5. Accept offer and create job
6. Test all relationships

---

## Database File

- **Location:** `backend/roadside_assistance.db`
- **Type:** SQLite
- **Auto-created:** Yes, on first run

To reset the database, simply delete the `.db` file and restart the application.

