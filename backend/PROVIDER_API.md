# 🔧 Provider API Documentation

## Overview

Provider-facing endpoints for managing profile, viewing nearby requests, sending offers, and managing jobs.

**Authentication Required:** All endpoints require a valid JWT token with `provider` role.

---

## Authentication

All requests must include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Get token from `/auth/verify-otp` endpoint with a provider user. See `AUTH.md` for details.

---

## Endpoints

### 1. Get Provider Profile

**Endpoint:** `GET /provider/profile`

**Description:** Get provider profile. Creates a minimal profile if none exists.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 2,
  "city": "San Francisco",
  "services_offered": "flat_tyre,jump_start,tow",
  "vehicle_types": "both",
  "is_verified": true,
  "average_rating": 4.8,
  "total_ratings": 45,
  "current_lat": 37.7749,
  "current_lng": -122.4194,
  "is_online": true
}
```

**Example (cURL):**
```bash
curl http://localhost:8000/provider/profile \
  -H "Authorization: Bearer <token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/provider/profile', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const profile = await response.json();
```

---

### 2. Update Provider Profile

**Endpoint:** `PUT /provider/profile`

**Description:** Update provider profile information. Creates profile if it doesn't exist.

**Request Body:**
```json
{
  "city": "San Francisco",
  "services_offered": "flat_tyre,jump_start,tow",
  "vehicle_types": "both",
  "is_online": true
}
```

**All fields are optional:**
- `city` - Operating city
- `services_offered` - Comma-separated: `flat_tyre,jump_start,fuel,tow,key_lock`
- `vehicle_types` - `car`, `bike`, or `both`
- `is_online` - Online/available status

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 2,
  "city": "San Francisco",
  "services_offered": "flat_tyre,jump_start,tow",
  "vehicle_types": "both",
  "is_verified": true,
  "average_rating": 4.8,
  "total_ratings": 45,
  "current_lat": 37.7749,
  "current_lng": -122.4194,
  "is_online": true
}
```

**Example (cURL):**
```bash
curl -X PUT http://localhost:8000/provider/profile \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "San Francisco",
    "services_offered": "flat_tyre,tow",
    "vehicle_types": "both",
    "is_online": true
  }'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/provider/profile', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    city: 'San Francisco',
    services_offered: 'flat_tyre,tow',
    vehicle_types: 'both',
    is_online: true
  })
});
const profile = await response.json();
```

---

### 3. Update Location

**Endpoint:** `POST /provider/location`

**Description:** Update provider's current location for geolocation-based matching.

**Request Body:**
```json
{
  "lat": 37.7749,
  "lng": -122.4194
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 2,
  "city": "San Francisco",
  "services_offered": "flat_tyre,jump_start,tow",
  "vehicle_types": "both",
  "is_verified": true,
  "average_rating": 4.8,
  "total_ratings": 45,
  "current_lat": 37.7749,
  "current_lng": -122.4194,
  "is_online": true
}
```

**Error Response:**

`404 Not Found` - Profile doesn't exist
```json
{
  "detail": "Provider profile not found. Please create profile first."
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/provider/location \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 37.7749,
    "lng": -122.4194
  }'
```

**Example (JavaScript):**
```javascript
// Update location (e.g., from GPS)
navigator.geolocation.getCurrentPosition(async (position) => {
  const response = await fetch('http://localhost:8000/provider/location', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      lat: position.coords.latitude,
      lng: position.coords.longitude
    })
  });
  const profile = await response.json();
  console.log('Location updated:', profile);
});
```

---

### 4. Get Nearby Requests

**Endpoint:** `GET /provider/nearby-requests`

**Description:** Get service requests within specified radius using geolocation.

Uses Haversine formula to calculate distances accurately.

**Query Parameters:**
- `radius_km` - Search radius in kilometers (default: 10.0, min: 0.1, max: 100.0)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "customer_id": 3,
    "service_type": "flat_tyre",
    "vehicle_type": "car",
    "description": "Flat tire on Highway 101",
    "price_offered": 75.0,
    "lat": 37.7849,
    "lng": -122.4094,
    "status": "pending_offers",
    "distance_km": 1.23,
    "created_at": "2025-12-01T12:00:00"
  },
  {
    "id": 2,
    "customer_id": 4,
    "service_type": "jump_start",
    "vehicle_type": "car",
    "description": "Dead battery at Mall parking",
    "price_offered": 50.0,
    "lat": 37.7649,
    "lng": -122.4294,
    "status": "pending_offers",
    "distance_km": 2.45,
    "created_at": "2025-12-01T12:15:00"
  }
]
```

**Results are sorted by distance (closest first).**

**Error Response:**

`400 Bad Request` - Location not set
```json
{
  "detail": "Provider location not set. Please update your location first using POST /provider/location"
}
```

**Example (cURL):**
```bash
# Default 10 km radius
curl http://localhost:8000/provider/nearby-requests \
  -H "Authorization: Bearer <token>"

# Custom 20 km radius
curl "http://localhost:8000/provider/nearby-requests?radius_km=20" \
  -H "Authorization: Bearer <token>"
```

**Example (JavaScript):**
```javascript
// Get requests within 15 km
const response = await fetch('http://localhost:8000/provider/nearby-requests?radius_km=15', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const requests = await response.json();

// Display on map
requests.forEach(request => {
  console.log(`${request.service_type} - ${request.distance_km} km away - $${request.price_offered}`);
});
```

---

### 5. Create Offer

**Endpoint:** `POST /provider/offers`

**Description:** Send an offer/bid on a service request.

**Request Body:**
```json
{
  "service_request_id": 1,
  "price": 65.0,
  "eta_minutes": 15
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "service_request_id": 1,
  "provider_id": 2,
  "price": 65.0,
  "eta_minutes": 15,
  "status": "pending",
  "created_at": "2025-12-01T12:05:00",
  "updated_at": "2025-12-01T12:05:00"
}
```

**Error Responses:**

`404 Not Found` - Request not found
```json
{
  "detail": "Service request not found"
}
```

`400 Bad Request` - Request not accepting offers
```json
{
  "detail": "Service request is not accepting offers. Current status: offer_selected"
}
```

`400 Bad Request` - Already sent offer
```json
{
  "detail": "You already have a pending offer on this request"
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/provider/offers \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "service_request_id": 1,
    "price": 65.0,
    "eta_minutes": 15
  }'
```

**Example (JavaScript):**
```javascript
async function sendOffer(requestId, price, eta) {
  const response = await fetch('http://localhost:8000/provider/offers', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      service_request_id: requestId,
      price: price,
      eta_minutes: eta
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}
```

---

### 6. Get Active Jobs

**Endpoint:** `GET /provider/jobs/active`

**Description:** Get all active jobs for the provider.

Returns jobs that are not completed or cancelled.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "service_request_id": 1,
    "offer_id": 1,
    "status": "on_the_way",
    "created_at": "2025-12-01T12:10:00",
    "updated_at": "2025-12-01T12:15:00",
    "service_request": {
      "id": 1,
      "customer_id": 3,
      "service_type": "flat_tyre",
      "vehicle_type": "car",
      "description": "Flat tire on Highway 101",
      "price_offered": 75.0,
      "lat": 37.7849,
      "lng": -122.4094,
      "status": "offer_selected",
      "created_at": "2025-12-01T12:00:00",
      "updated_at": "2025-12-01T12:10:00"
    },
    "offer": {
      "id": 1,
      "service_request_id": 1,
      "provider_id": 2,
      "price": 65.0,
      "eta_minutes": 15,
      "status": "accepted",
      "created_at": "2025-12-01T12:05:00",
      "updated_at": "2025-12-01T12:10:00",
      "provider": {
        "id": 2,
        "name": "John's Towing",
        "phone": "+0987654321",
        "provider_profile": {
          "id": 1,
          "user_id": 2,
          "city": "San Francisco",
          "services_offered": "flat_tyre,tow",
          "vehicle_types": "both",
          "is_verified": true,
          "average_rating": 4.8,
          "total_ratings": 45,
          "current_lat": 37.7749,
          "current_lng": -122.4194,
          "is_online": true
        }
      }
    }
  }
]
```

**Example (cURL):**
```bash
curl http://localhost:8000/provider/jobs/active \
  -H "Authorization: Bearer <token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/provider/jobs/active', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const activeJobs = await response.json();

console.log(`You have ${activeJobs.length} active jobs`);
```

---

### 7. Update Job Status

**Endpoint:** `PATCH /provider/jobs/{job_id}/status`

**Description:** Update job status to track progress.

**Path Parameters:**
- `job_id` - Job ID

**Request Body:**
```json
{
  "status": "on_the_way"
}
```

**Valid Job Statuses:**
- `assigned` - Job assigned (initial status)
- `on_the_way` - Provider is en route
- `arrived` - Provider has arrived at location
- `in_progress` - Service is being performed
- `completed` - Job successfully completed
- `cancelled` - Job was cancelled

**Response:** `200 OK`
```json
{
  "id": 1,
  "service_request_id": 1,
  "offer_id": 1,
  "status": "on_the_way",
  "created_at": "2025-12-01T12:10:00",
  "updated_at": "2025-12-01T12:15:00",
  "service_request": {...},
  "offer": {...}
}
```

**Error Responses:**

`404 Not Found` - Job not found
```json
{
  "detail": "Job not found"
}
```

`403 Forbidden` - Job doesn't belong to provider
```json
{
  "detail": "Access denied. This job does not belong to you."
}
```

`400 Bad Request` - Invalid status
```json
{
  "detail": "Invalid status. Must be one of: assigned, on_the_way, arrived, in_progress, completed, cancelled"
}
```

**Example (cURL):**
```bash
curl -X PATCH http://localhost:8000/provider/jobs/1/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "on_the_way"}'
```

**Example (JavaScript):**
```javascript
async function updateJobStatus(jobId, status) {
  const response = await fetch(`http://localhost:8000/provider/jobs/${jobId}/status`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status })
  });
  return await response.json();
}

// Usage
await updateJobStatus(1, 'on_the_way');
await updateJobStatus(1, 'arrived');
await updateJobStatus(1, 'in_progress');
await updateJobStatus(1, 'completed');
```

---

## Complete Provider Flow

### 1. Provider Setup

```javascript
// Login as provider
const authResponse = await fetch('http://localhost:8000/auth/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+0987654321',
    otp: '1234',
    name: "John's Towing"
  })
});
const { access_token } = await authResponse.json();

// Update profile
await fetch('http://localhost:8000/provider/profile', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    city: 'San Francisco',
    services_offered: 'flat_tyre,jump_start,tow',
    vehicle_types: 'both',
    is_online: true
  })
});

// Update location
await fetch('http://localhost:8000/provider/location', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    lat: 37.7749,
    lng: -122.4194
  })
});
```

### 2. Find and Bid on Requests

```javascript
// Get nearby requests
const requestsResponse = await fetch(
  'http://localhost:8000/provider/nearby-requests?radius_km=15',
  {
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
const nearbyRequests = await requestsResponse.json();

// Send offer on best request
const bestRequest = nearbyRequests[0]; // Closest request
const offerResponse = await fetch('http://localhost:8000/provider/offers', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_request_id: bestRequest.id,
    price: bestRequest.price_offered * 0.9, // Offer 10% discount
    eta_minutes: Math.ceil(bestRequest.distance_km * 3) // 3 min per km
  })
});
```

### 3. Manage Active Jobs

```javascript
// Check for active jobs
const jobsResponse = await fetch('http://localhost:8000/provider/jobs/active', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const activeJobs = await jobsResponse.json();

if (activeJobs.length > 0) {
  const job = activeJobs[0];
  
  // Update status as you progress
  await updateJobStatus(job.id, 'on_the_way');
  
  // ... drive to location ...
  
  await updateJobStatus(job.id, 'arrived');
  
  // ... perform service ...
  
  await updateJobStatus(job.id, 'in_progress');
  
  // ... complete service ...
  
  await updateJobStatus(job.id, 'completed');
}
```

### 4. Poll for New Requests

```javascript
// Poll every 30 seconds for new nearby requests
setInterval(async () => {
  const response = await fetch(
    'http://localhost:8000/provider/nearby-requests?radius_km=15',
    {
      headers: { 'Authorization': `Bearer ${access_token}` }
    }
  );
  const requests = await response.json();
  
  // Notify provider of new requests
  requests.forEach(request => {
    showNotification(
      `New ${request.service_type} request - $${request.price_offered} - ${request.distance_km} km away`
    );
  });
}, 30000);
```

---

## Geolocation Features

### Distance Calculation

The API uses the **Haversine formula** to calculate accurate distances between provider and requests:

```
Distance = 2 * R * arcsin(sqrt(sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)))
```

Where R = 6371 km (Earth's radius)

### Accuracy
- ✅ Accurate within meters for short distances
- ✅ Accurate within kilometers for long distances
- ✅ Works worldwide (considers Earth's curvature)

### Location Updates
- Update location frequently for accurate matching
- Recommended: Update every 30-60 seconds when online
- Use device GPS for best accuracy

---

## Error Handling

### Common Error Codes

- `400 Bad Request` - Invalid input or business logic error
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Not a provider or wrong ownership
- `404 Not Found` - Resource not found

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Example Error Handling

```javascript
try {
  const response = await fetch('http://localhost:8000/provider/offers', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(offerData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    
    if (error.detail.includes('already have a pending offer')) {
      alert('You already sent an offer on this request');
    } else if (error.detail.includes('not accepting offers')) {
      alert('This request is no longer available');
    } else {
      throw new Error(error.detail);
    }
  }
  
  const offer = await response.json();
  return offer;
} catch (error) {
  console.error('Failed to create offer:', error.message);
}
```

---

## Best Practices

### Location Updates
```javascript
// Update location periodically when online
if (providerProfile.is_online) {
  setInterval(() => {
    navigator.geolocation.getCurrentPosition(async (position) => {
      await fetch('http://localhost:8000/provider/location', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        })
      });
    });
  }, 60000); // Every minute
}
```

### Competitive Pricing
```javascript
// Calculate competitive price based on distance
function calculatePrice(basePrice, distanceKm) {
  const travelCost = distanceKm * 2; // $2 per km
  const serviceCost = basePrice * 0.8; // 20% discount
  return Math.round(travelCost + serviceCost);
}
```

### ETA Calculation
```javascript
// Calculate realistic ETA
function calculateETA(distanceKm) {
  const avgSpeed = 40; // km/h in city
  const minutes = Math.ceil((distanceKm / avgSpeed) * 60);
  return Math.max(minutes, 5); // Minimum 5 minutes
}
```

---

## Testing with Swagger UI

1. Start backend: `uvicorn backend.main:app --reload`
2. Visit: http://localhost:8000/docs
3. Click **Authorize** button
4. Enter: `Bearer <provider-token>`
5. Try provider endpoints under **Provider** tag

---

## See Also

- `AUTH.md` - Authentication documentation
- `CUSTOMER_API.md` - Customer API documentation
- `DATABASE.md` - Data model documentation

