# 📊 Admin API Documentation

## Overview

Admin-facing endpoints for system monitoring and management. Provides read-only access to all system data with basic management capabilities.

**Authentication Required:** All endpoints require a valid JWT token with `admin` role.

---

## Authentication

All requests must include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Get token from `/auth/verify-otp` endpoint with an admin user. See `AUTH.md` for details.

**Note:** To create an admin user, you'll need to manually update a user's role in the database or implement a separate admin creation endpoint.

---

## Endpoints

### 1. List Users

**Endpoint:** `GET /admin/users`

**Description:** Get list of all users with optional role filter.

**Query Parameters:**
- `role` (optional) - Filter by role: `customer`, `provider`, or `admin`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "phone": "+1234567890",
    "role": "customer",
    "created_at": "2025-12-01T10:00:00"
  },
  {
    "id": 2,
    "name": "Jane's Towing",
    "phone": "+0987654321",
    "role": "provider",
    "created_at": "2025-12-01T11:00:00"
  }
]
```

**Example (cURL):**
```bash
# All users
curl http://localhost:8000/admin/users \
  -H "Authorization: Bearer <admin-token>"

# Only customers
curl "http://localhost:8000/admin/users?role=customer" \
  -H "Authorization: Bearer <admin-token>"

# Only providers
curl "http://localhost:8000/admin/users?role=provider" \
  -H "Authorization: Bearer <admin-token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/admin/users?role=provider', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});
const users = await response.json();
console.log(`Total providers: ${users.length}`);
```

---

### 2. List Providers

**Endpoint:** `GET /admin/providers`

**Description:** Get list of all provider profiles with user information.

**Response:** `200 OK`
```json
[
  {
    "provider_profile_id": 1,
    "user_id": 2,
    "user_name": "Jane's Towing",
    "user_phone": "+0987654321",
    "city": "San Francisco",
    "services_offered": "flat_tyre,jump_start,tow",
    "vehicle_types": "both",
    "is_verified": true,
    "is_online": true,
    "average_rating": 4.8,
    "total_ratings": 45
  },
  {
    "provider_profile_id": 2,
    "user_id": 5,
    "user_name": "Bob's Garage",
    "user_phone": "+1122334455",
    "city": "Oakland",
    "services_offered": "flat_tyre,jump_start",
    "vehicle_types": "car",
    "is_verified": false,
    "is_online": false,
    "average_rating": 5.0,
    "total_ratings": 0
  }
]
```

**Example (cURL):**
```bash
curl http://localhost:8000/admin/providers \
  -H "Authorization: Bearer <admin-token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/admin/providers', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});
const providers = await response.json();

// Find unverified providers
const unverified = providers.filter(p => !p.is_verified);
console.log(`${unverified.length} providers need verification`);
```

---

### 3. Update Provider Verification

**Endpoint:** `PATCH /admin/providers/{provider_profile_id}`

**Description:** Update provider verification status.

**Path Parameters:**
- `provider_profile_id` - Provider profile ID

**Request Body:**
```json
{
  "is_verified": true
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
  "is_online": true,
  "average_rating": 4.8,
  "total_ratings": 45,
  "current_lat": 37.7749,
  "current_lng": -122.4194
}
```

**Error Response:**

`404 Not Found` - Provider profile not found
```json
{
  "detail": "Provider profile not found"
}
```

**Example (cURL):**
```bash
# Verify provider
curl -X PATCH http://localhost:8000/admin/providers/1 \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"is_verified": true}'

# Unverify provider
curl -X PATCH http://localhost:8000/admin/providers/1 \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"is_verified": false}'
```

**Example (JavaScript):**
```javascript
async function verifyProvider(profileId, verified) {
  const response = await fetch(`http://localhost:8000/admin/providers/${profileId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ is_verified: verified })
  });
  return await response.json();
}

// Verify a provider
await verifyProvider(1, true);
```

---

### 4. List Service Requests

**Endpoint:** `GET /admin/service-requests`

**Description:** Get list of service requests with offer counts.

**Query Parameters:**
- `status` (optional) - Filter by status: `pending_offers`, `offer_selected`, `cancelled`, `expired`
- `customer_id` (optional) - Filter by customer ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "customer_id": 3,
    "customer_name": "John Doe",
    "service_type": "flat_tyre",
    "vehicle_type": "car",
    "description": "Flat tire on Highway 101",
    "price_offered": 75.0,
    "lat": 37.7849,
    "lng": -122.4094,
    "status": "offer_selected",
    "offer_count": 3,
    "created_at": "2025-12-01T12:00:00",
    "updated_at": "2025-12-01T12:10:00"
  },
  {
    "id": 2,
    "customer_id": 4,
    "customer_name": "Alice Smith",
    "service_type": "jump_start",
    "vehicle_type": "car",
    "description": "Dead battery",
    "price_offered": 50.0,
    "lat": 37.7649,
    "lng": -122.4294,
    "status": "pending_offers",
    "offer_count": 1,
    "created_at": "2025-12-01T12:15:00",
    "updated_at": "2025-12-01T12:15:00"
  }
]
```

**Example (cURL):**
```bash
# All requests
curl http://localhost:8000/admin/service-requests \
  -H "Authorization: Bearer <admin-token>"

# Pending requests only
curl "http://localhost:8000/admin/service-requests?status=pending_offers" \
  -H "Authorization: Bearer <admin-token>"

# Requests for specific customer
curl "http://localhost:8000/admin/service-requests?customer_id=5" \
  -H "Authorization: Bearer <admin-token>"

# Combined filters
curl "http://localhost:8000/admin/service-requests?status=offer_selected&customer_id=3" \
  -H "Authorization: Bearer <admin-token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/admin/service-requests?status=pending_offers', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});
const requests = await response.json();

// Calculate stats
const totalOffers = requests.reduce((sum, r) => sum + r.offer_count, 0);
console.log(`${requests.length} pending requests with ${totalOffers} total offers`);
```

---

### 5. List Jobs

**Endpoint:** `GET /admin/jobs`

**Description:** Get list of jobs with related information.

**Query Parameters:**
- `status` (optional) - Filter by status: `assigned`, `on_the_way`, `arrived`, `in_progress`, `completed`, `cancelled`

**Response:** `200 OK`
```json
[
  {
    "job_id": 1,
    "job_status": "in_progress",
    "job_created_at": "2025-12-01T12:10:00",
    "job_updated_at": "2025-12-01T12:30:00",
    "service_request_id": 1,
    "service_type": "flat_tyre",
    "vehicle_type": "car",
    "customer_id": 3,
    "customer_name": "John Doe",
    "provider_id": 2,
    "provider_name": "Jane's Towing"
  },
  {
    "job_id": 2,
    "job_status": "completed",
    "job_created_at": "2025-12-01T10:00:00",
    "job_updated_at": "2025-12-01T11:00:00",
    "service_request_id": 5,
    "service_type": "jump_start",
    "vehicle_type": "car",
    "customer_id": 8,
    "customer_name": "Bob Miller",
    "provider_id": 2,
    "provider_name": "Jane's Towing"
  }
]
```

**Example (cURL):**
```bash
# All jobs
curl http://localhost:8000/admin/jobs \
  -H "Authorization: Bearer <admin-token>"

# Active jobs only
curl "http://localhost:8000/admin/jobs?status=in_progress" \
  -H "Authorization: Bearer <admin-token>"

# Completed jobs
curl "http://localhost:8000/admin/jobs?status=completed" \
  -H "Authorization: Bearer <admin-token>"
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/admin/jobs', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});
const jobs = await response.json();

// Calculate completion rate
const completed = jobs.filter(j => j.job_status === 'completed').length;
const cancelled = jobs.filter(j => j.job_status === 'cancelled').length;
const completionRate = (completed / (completed + cancelled) * 100).toFixed(1);
console.log(`Completion rate: ${completionRate}%`);
```

---

## Complete Admin Dashboard Example

### React Admin Dashboard

```typescript
// components/AdminDashboard.tsx
import { useEffect, useState } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
  }
});

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalProviders: 0,
    unverifiedProviders: 0,
    pendingRequests: 0,
    activeJobs: 0,
    completedJobs: 0
  });

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    // Get all data
    const [users, providers, requests, jobs] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/providers'),
      api.get('/admin/service-requests'),
      api.get('/admin/jobs')
    ]);

    setStats({
      totalUsers: users.data.length,
      totalProviders: providers.data.length,
      unverifiedProviders: providers.data.filter(p => !p.is_verified).length,
      pendingRequests: requests.data.filter(r => r.status === 'pending_offers').length,
      activeJobs: jobs.data.filter(j => !['completed', 'cancelled'].includes(j.job_status)).length,
      completedJobs: jobs.data.filter(j => j.job_status === 'completed').length
    });
  }

  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      
      <div className="stats-grid">
        <StatCard title="Total Users" value={stats.totalUsers} />
        <StatCard title="Providers" value={stats.totalProviders} />
        <StatCard title="Unverified Providers" value={stats.unverifiedProviders} alert />
        <StatCard title="Pending Requests" value={stats.pendingRequests} />
        <StatCard title="Active Jobs" value={stats.activeJobs} />
        <StatCard title="Completed Jobs" value={stats.completedJobs} />
      </div>

      <div className="admin-sections">
        <ProvidersSection />
        <RequestsSection />
        <JobsSection />
      </div>
    </div>
  );
}

function ProvidersSection() {
  const [providers, setProviders] = useState([]);

  useEffect(() => {
    api.get('/admin/providers').then(res => setProviders(res.data));
  }, []);

  async function toggleVerification(provider) {
    await api.patch(`/admin/providers/${provider.provider_profile_id}`, {
      is_verified: !provider.is_verified
    });
    // Reload
    const res = await api.get('/admin/providers');
    setProviders(res.data);
  }

  return (
    <section>
      <h2>Providers</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>City</th>
            <th>Services</th>
            <th>Rating</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {providers.map(provider => (
            <tr key={provider.provider_profile_id}>
              <td>{provider.user_name}</td>
              <td>{provider.city || 'N/A'}</td>
              <td>{provider.services_offered || 'N/A'}</td>
              <td>{provider.average_rating.toFixed(1)} ({provider.total_ratings})</td>
              <td>
                {provider.is_verified ? '✓ Verified' : '⚠ Unverified'}
                {provider.is_online && ' • Online'}
              </td>
              <td>
                <button onClick={() => toggleVerification(provider)}>
                  {provider.is_verified ? 'Unverify' : 'Verify'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
```

---

## Analytics Examples

### Get System Statistics

```javascript
async function getSystemStats(adminToken) {
  const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });

  const [users, providers, requests, jobs] = await Promise.all([
    api.get('/admin/users'),
    api.get('/admin/providers'),
    api.get('/admin/service-requests'),
    api.get('/admin/jobs')
  ]);

  return {
    users: {
      total: users.data.length,
      customers: users.data.filter(u => u.role === 'customer').length,
      providers: users.data.filter(u => u.role === 'provider').length,
      admins: users.data.filter(u => u.role === 'admin').length
    },
    providers: {
      total: providers.data.length,
      verified: providers.data.filter(p => p.is_verified).length,
      online: providers.data.filter(p => p.is_online).length,
      avgRating: (providers.data.reduce((sum, p) => sum + p.average_rating, 0) / providers.data.length).toFixed(2)
    },
    requests: {
      total: requests.data.length,
      pending: requests.data.filter(r => r.status === 'pending_offers').length,
      selected: requests.data.filter(r => r.status === 'offer_selected').length,
      avgOffers: (requests.data.reduce((sum, r) => sum + r.offer_count, 0) / requests.data.length).toFixed(1)
    },
    jobs: {
      total: jobs.data.length,
      active: jobs.data.filter(j => !['completed', 'cancelled'].includes(j.job_status)).length,
      completed: jobs.data.filter(j => j.job_status === 'completed').length,
      cancelled: jobs.data.filter(j => j.job_status === 'cancelled').length
    }
  };
}
```

---

## Error Handling

### Common Error Codes

- `400 Bad Request` - Invalid status/role filter
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Not an admin
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
  const response = await fetch('http://localhost:8000/admin/users?role=invalid', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    if (error.detail.includes('Invalid role')) {
      alert('Please use: customer, provider, or admin');
    }
  }
} catch (error) {
  console.error('Admin API error:', error);
}
```

---

## Security Notes

### Creating Admin Users

Admin users must be created manually or through a secure process:

**Option 1: Manual Database Update**
```sql
UPDATE users SET role = 'admin' WHERE phone = '+1234567890';
```

**Option 2: Secure Registration Endpoint (Recommended)**
```python
# Only implement this with proper authentication
@app.post("/admin/create-admin")
def create_admin(
    user_data: dict,
    master_key: str = Header(...),
    db: Session = Depends(get_db)
):
    if master_key != settings.MASTER_ADMIN_KEY:
        raise HTTPException(status_code=403)
    # Create admin user
```

### Best Practices

- ✅ Use strong admin passwords/keys
- ✅ Log all admin actions
- ✅ Limit admin access to specific IPs (if possible)
- ✅ Implement audit trails
- ✅ Regular security reviews

---

## Testing with Swagger UI

1. Start backend: `uvicorn backend.main:app --reload`
2. Visit: http://localhost:8000/docs
3. Click **Authorize** button
4. Enter: `Bearer <admin-token>`
5. Try admin endpoints under **Admin** tag

---

## See Also

- `AUTH.md` - Authentication documentation
- `CUSTOMER_API.md` - Customer API documentation
- `PROVIDER_API.md` - Provider API documentation
- `DATABASE.md` - Data model documentation

