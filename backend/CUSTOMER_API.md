# 👥 Customer API Documentation

## Overview

Customer-facing endpoints for creating service requests, viewing offers, and managing jobs.

**Authentication Required:** All endpoints require a valid JWT token with `customer` role.

---

## Authentication

All requests must include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Get token from `/auth/verify-otp` endpoint. See `AUTH.md` for details.

---

## Endpoints

### 1. Create Service Request

**Endpoint:** `POST /customer/service-requests`

**Description:** Create a new roadside assistance request.

**Request Body:**
```json
{
  "service_type": "flat_tyre",
  "vehicle_type": "car",
  "description": "Flat tire on Highway 101, near Exit 45",
  "price_offered": 75.0,
  "lat": 37.7749,
  "lng": -122.4194
}
```

**Service Types:**
- `flat_tyre` - Flat tire repair/replacement
- `jump_start` - Battery jump start
- `fuel` - Fuel delivery
- `tow` - Vehicle towing
- `key_lock` - Lockout assistance
- `other` - Other services

**Vehicle Types:**
- `car` - Automobile
- `bike` - Motorcycle

**Response:** `201 Created`
```json
{
  "id": 1,
  "customer_id": 1,
  "service_type": "flat_tyre",
  "vehicle_type": "car",
  "description": "Flat tire on Highway 101, near Exit 45",
  "price_offered": 75.0,
  "lat": 37.7749,
  "lng": -122.4194,
  "status": "pending_offers",
  "created_at": "2025-12-01T12:00:00",
  "updated_at": "2025-12-01T12:00:00"
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/customer/service-requests \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "flat_tyre",
    "vehicle_type": "car",
    "description": "Flat tire on Highway 101",
    "price_offered": 75.0,
    "lat": 37.7749,
    "lng": -122.4194
  }'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/customer/service-requests', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_type: 'flat_tyre',
    vehicle_type: 'car',
    description: 'Flat tire on Highway 101',
    price_offered: 75.0,
    lat: 37.7749,
    lng: -122.4194
  })
});
const request = await response.json();
```

---

### 2. Get Service Request Details

**Endpoint:** `GET /customer/service-requests/{request_id}`

**Description:** Get a service request with all offers and job details.

**Path Parameters:**
- `request_id` - Service request ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "customer_id": 1,
  "service_type": "flat_tyre",
  "vehicle_type": "car",
  "description": "Flat tire on Highway 101",
  "price_offered": 75.0,
  "lat": 37.7749,
  "lng": -122.4194,
  "status": "pending_offers",
  "created_at": "2025-12-01T12:00:00",
  "updated_at": "2025-12-01T12:00:00",
  "offers": [
    {
      "id": 1,
      "service_request_id": 1,
      "provider_id": 2,
      "price": 65.0,
      "eta_minutes": 15,
      "status": "pending",
      "created_at": "2025-12-01T12:05:00",
      "updated_at": "2025-12-01T12:05:00",
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
          "current_lat": 37.7649,
          "current_lng": -122.4294,
          "is_online": true
        }
      }
    }
  ],
  "job": null
}
```

**Error Responses:**

`404 Not Found` - Request not found
```json
{
  "detail": "Service request not found"
}
```

`403 Forbidden` - Request doesn't belong to customer
```json
{
  "detail": "Access denied. This request does not belong to you."
}
```

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/customer/service-requests/1 \
  -H "Authorization: Bearer <token>"
```

---

### 3. Get Active Request

**Endpoint:** `GET /customer/active-request`

**Description:** Get the most recent active service request for the current customer.

Returns requests with status `pending_offers` or `offer_selected`.

**Response:** `200 OK`

If active request exists:
```json
{
  "id": 1,
  "customer_id": 1,
  "service_type": "flat_tyre",
  "vehicle_type": "car",
  "description": "Flat tire on Highway 101",
  "price_offered": 75.0,
  "lat": 37.7749,
  "lng": -122.4194,
  "status": "pending_offers",
  "created_at": "2025-12-01T12:00:00",
  "updated_at": "2025-12-01T12:00:00",
  "offers": [...],
  "job": null
}
```

If no active request:
```json
null
```

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/customer/active-request \
  -H "Authorization: Bearer <token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/customer/active-request', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const activeRequest = await response.json();

if (activeRequest) {
  console.log('Active request:', activeRequest);
} else {
  console.log('No active request');
}
```

---

### 4. Accept Offer

**Endpoint:** `POST /customer/offers/{offer_id}/accept`

**Description:** Accept a provider's offer and create a job.

**What happens:**
1. ✅ Selected offer status → `accepted`
2. ❌ Other offers → `rejected`
3. 📝 Request status → `offer_selected`
4. 🚀 New job created with status `assigned`

**Path Parameters:**
- `offer_id` - Offer ID to accept

**Response:** `200 OK`
```json
{
  "id": 1,
  "service_request_id": 1,
  "offer_id": 1,
  "status": "assigned",
  "created_at": "2025-12-01T12:10:00",
  "updated_at": "2025-12-01T12:10:00",
  "service_request": {
    "id": 1,
    "customer_id": 1,
    "service_type": "flat_tyre",
    "vehicle_type": "car",
    "description": "Flat tire on Highway 101",
    "price_offered": 75.0,
    "lat": 37.7749,
    "lng": -122.4194,
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
        "current_lat": 37.7649,
        "current_lng": -122.4294,
        "is_online": true
      }
    }
  }
}
```

**Error Responses:**

`404 Not Found` - Offer not found
```json
{
  "detail": "Offer not found"
}
```

`403 Forbidden` - Request doesn't belong to customer
```json
{
  "detail": "Access denied. This request does not belong to you."
}
```

`400 Bad Request` - Invalid offer state
```json
{
  "detail": "Cannot accept offer with status 'accepted'. Offer must be pending."
}
```

`400 Bad Request` - Invalid request state
```json
{
  "detail": "Cannot accept offer. Request status is 'offer_selected'. Must be 'pending_offers'."
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/customer/offers/1/accept \
  -H "Authorization: Bearer <token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch(`http://localhost:8000/customer/offers/${offerId}/accept`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const job = await response.json();
console.log('Job created:', job);
```

---

### 5. Get Job Details

**Endpoint:** `GET /customer/jobs/{job_id}`

**Description:** Get job details with provider information and current location.

**Path Parameters:**
- `job_id` - Job ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "service_request_id": 1,
  "offer_id": 1,
  "status": "on_the_way",
  "created_at": "2025-12-01T12:10:00",
  "updated_at": "2025-12-01T12:15:00",
  "service_request": {
    "id": 1,
    "customer_id": 1,
    "service_type": "flat_tyre",
    "vehicle_type": "car",
    "description": "Flat tire on Highway 101",
    "price_offered": 75.0,
    "lat": 37.7749,
    "lng": -122.4194,
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
        "current_lat": 37.7699,
        "current_lng": -122.4244,
        "is_online": true
      }
    }
  }
}
```

**Job Statuses:**
- `assigned` - Provider assigned to job
- `on_the_way` - Provider en route
- `arrived` - Provider at location
- `in_progress` - Service in progress
- `completed` - Job completed
- `cancelled` - Job cancelled

**Error Responses:**

`404 Not Found` - Job not found
```json
{
  "detail": "Job not found"
}
```

`403 Forbidden` - Job doesn't belong to customer
```json
{
  "detail": "Access denied. This job does not belong to you."
}
```

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/customer/jobs/1 \
  -H "Authorization: Bearer <token>"
```

---

## Complete User Flow

### 1. Customer Creates Request

```javascript
// Login first
const authResponse = await fetch('http://localhost:8000/auth/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+1234567890',
    otp: '1234',
    name: 'Jane Doe'
  })
});
const { access_token } = await authResponse.json();

// Create service request
const requestResponse = await fetch('http://localhost:8000/customer/service-requests', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_type: 'flat_tyre',
    vehicle_type: 'car',
    description: 'Flat tire on Highway 101',
    price_offered: 75.0,
    lat: 37.7749,
    lng: -122.4194
  })
});
const request = await requestResponse.json();
console.log('Request created:', request.id);
```

### 2. Poll for Offers

```javascript
// Check for offers periodically
async function checkOffers(requestId) {
  const response = await fetch(
    `http://localhost:8000/customer/service-requests/${requestId}`,
    {
      headers: { 'Authorization': `Bearer ${access_token}` }
    }
  );
  const request = await response.json();
  return request.offers;
}

// Poll every 5 seconds
const pollInterval = setInterval(async () => {
  const offers = await checkOffers(request.id);
  if (offers.length > 0) {
    console.log('Received offers:', offers);
    clearInterval(pollInterval);
  }
}, 5000);
```

### 3. Accept Best Offer

```javascript
// Customer selects best offer
const bestOffer = offers.reduce((prev, current) => 
  current.price < prev.price ? current : prev
);

const acceptResponse = await fetch(
  `http://localhost:8000/customer/offers/${bestOffer.id}/accept`,
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
const job = await acceptResponse.json();
console.log('Job created:', job.id);
```

### 4. Track Provider

```javascript
// Poll job status and provider location
async function trackProvider(jobId) {
  const response = await fetch(
    `http://localhost:8000/customer/jobs/${jobId}`,
    {
      headers: { 'Authorization': `Bearer ${access_token}` }
    }
  );
  const job = await response.json();
  
  console.log('Job status:', job.status);
  console.log('Provider location:', {
    lat: job.offer.provider.provider_profile.current_lat,
    lng: job.offer.provider.provider_profile.current_lng
  });
  
  return job;
}

// Poll every 10 seconds
const trackInterval = setInterval(async () => {
  const job = await trackProvider(job.id);
  
  if (job.status === 'completed') {
    console.log('Job completed!');
    clearInterval(trackInterval);
  }
}, 10000);
```

---

## Error Handling

### Common Error Codes

- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Not a customer or wrong role
- `404 Not Found` - Resource not found
- `400 Bad Request` - Invalid input or state

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Example Error Handling

```javascript
try {
  const response = await fetch('http://localhost:8000/customer/service-requests', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('Failed to create request:', error.message);
  
  if (error.message.includes('validate credentials')) {
    // Token expired, redirect to login
    window.location.href = '/login';
  }
}
```

---

## Testing with Swagger UI

1. Start backend: `uvicorn backend.main:app --reload`
2. Visit: http://localhost:8000/docs
3. Click **Authorize** button
4. Enter: `Bearer <your-token>`
5. Try customer endpoints under **Customer** tag

---

## See Also

- `AUTH.md` - Authentication documentation
- `DATABASE.md` - Data model documentation
- `QUICK_REFERENCE.md` - Backend quick reference

