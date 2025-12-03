# 🔐 Authentication System Documentation

## Overview

The Roadside Assistance Marketplace uses a phone + OTP (One-Time Password) authentication system with JWT (JSON Web Tokens) for session management.

**Demo Mode:** For development purposes, the OTP is always `"1234"`. No actual SMS is sent.

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. POST /auth/request-otp
       │    { "phone": "+123456" }
       ▼
┌─────────────┐
│  Backend    │──── Returns: { "demoOtp": "1234" }
└──────┬──────┘
       │
       │ 2. POST /auth/verify-otp
       │    { "phone": "+123456", "otp": "1234" }
       ▼
┌─────────────┐
│  Database   │──── Find/Create User
└──────┬──────┘
       │
       ▼
   JWT Token ───► Client stores token
       │
       │ 3. Protected requests
       │    Authorization: Bearer <token>
       ▼
  Validate & access user data
```

---

## API Endpoints

### 1. Request OTP

**Endpoint:** `POST /auth/request-otp`

**Description:** Request an OTP for phone number authentication.

**Request Body:**
```json
{
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "message": "OTP sent",
  "demoOtp": "1234"
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/auth/request-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+1234567890' })
});
const data = await response.json();
console.log(data.demoOtp); // "1234"
```

---

### 2. Verify OTP and Login

**Endpoint:** `POST /auth/verify-otp`

**Description:** Verify OTP and receive JWT access token.

- **Existing users:** Logs them in
- **New users:** Creates account with customer role

**Request Body:**
```json
{
  "phone": "+1234567890",
  "otp": "1234",
  "name": "John Doe"  // Optional, only for new users
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
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

**Error Response (Invalid OTP):**
```json
{
  "detail": "Invalid OTP"
}
```
Status: 400 Bad Request

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "otp": "1234", "name": "John Doe"}'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/auth/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+1234567890',
    otp: '1234',
    name: 'John Doe'
  })
});
const data = await response.json();
const token = data.access_token;
localStorage.setItem('token', token);
```

---

### 3. Get Current User (Protected)

**Endpoint:** `GET /me`

**Description:** Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "+1234567890",
  "role": "customer",
  "created_at": "2025-12-01T00:00:00",
  "updated_at": "2025-12-01T00:00:00"
}
```

**Error Response (No Token):**
```json
{
  "detail": "Not authenticated"
}
```
Status: 403 Forbidden

**Error Response (Invalid Token):**
```json
{
  "detail": "Could not validate credentials"
}
```
Status: 401 Unauthorized

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Example (JavaScript):**
```javascript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const user = await response.json();
```

---

## JWT Token Structure

### Token Payload

```json
{
  "sub": "1",                    // User ID
  "role": "customer",            // User role
  "phone": "+1234567890",        // Phone number
  "exp": 1701388800              // Expiration timestamp
}
```

### Configuration

Set via environment variables or use defaults:

```bash
# .env file
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Defaults:**
- `JWT_SECRET`: `"devsecret"` (⚠️ Change in production!)
- `JWT_ALGORITHM`: `"HS256"`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`

---

## Role-Based Access Control

### Available Roles

1. **customer** - Default for new users
2. **provider** - Service providers (mechanics, tow trucks)
3. **admin** - System administrators

### Authentication Dependencies

Use these in FastAPI route handlers:

#### 1. `get_current_user` - Any authenticated user

```python
from fastapi import Depends
from backend.deps import get_current_user
from backend.models import User

@app.get("/protected")
def protected_route(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "role": user.role}
```

#### 2. `get_current_customer` - Customer only

```python
from backend.deps import get_current_customer

@app.get("/customer-only")
def customer_route(user: User = Depends(get_current_customer)):
    return {"message": "Customer access granted"}
```

Returns 403 Forbidden if user is not a customer.

#### 3. `get_current_provider` - Provider only

```python
from backend.deps import get_current_provider

@app.get("/provider-only")
def provider_route(user: User = Depends(get_current_provider)):
    return {"message": "Provider access granted"}
```

Returns 403 Forbidden if user is not a provider.

#### 4. `get_current_admin` - Admin only

```python
from backend.deps import get_current_admin

@app.get("/admin-only")
def admin_route(user: User = Depends(get_current_admin)):
    return {"message": "Admin access granted"}
```

Returns 403 Forbidden if user is not an admin.

#### 5. `get_current_user_optional` - Optional authentication

```python
from backend.deps import get_current_user_optional
from typing import Optional

@app.get("/public-or-private")
def mixed_route(user: Optional[User] = Depends(get_current_user_optional)):
    if user:
        return {"message": f"Hello, {user.name}"}
    return {"message": "Hello, guest"}
```

---

## Frontend Integration

### Complete Auth Flow (React/Next.js)

```typescript
// 1. Request OTP
async function requestOTP(phone: string) {
  const response = await fetch('http://localhost:8000/auth/request-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });
  const data = await response.json();
  console.log('Demo OTP:', data.demoOtp);
}

// 2. Verify OTP and Login
async function verifyOTP(phone: string, otp: string, name?: string) {
  const response = await fetch('http://localhost:8000/auth/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, otp, name })
  });
  
  if (!response.ok) {
    throw new Error('Invalid OTP');
  }
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
}

// 3. Make authenticated requests
async function fetchProtectedData() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    // Token expired or invalid
    localStorage.removeItem('token');
    // Redirect to login
  }
  
  return await response.json();
}

// 4. Logout
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  // Redirect to login page
}
```

### Axios Interceptor Example

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Add token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (token expired)
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Security Considerations

### Development (Current Setup)

- ✅ JWT tokens with expiration
- ✅ HTTPS not required (localhost)
- ⚠️ Demo OTP "1234" (not secure)
- ⚠️ Default JWT_SECRET (change for production)

### Production Recommendations

1. **Environment Variables**
   ```bash
   JWT_SECRET=<strong-random-string>
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

2. **Real OTP System**
   - Generate random 6-digit OTP
   - Store in Redis with 5-minute expiry
   - Send via SMS (Twilio, AWS SNS, etc.)
   - Rate limiting on OTP requests

3. **HTTPS Only**
   - Enforce HTTPS in production
   - Use secure cookies for token storage

4. **Token Refresh**
   - Implement refresh tokens
   - Short-lived access tokens (15 min)
   - Long-lived refresh tokens (7 days)

5. **Additional Security**
   - Rate limiting on auth endpoints
   - Account lockout after failed attempts
   - IP-based restrictions
   - Device fingerprinting

---

## Testing the Auth System

### Using cURL

```bash
# 1. Request OTP
curl -X POST http://localhost:8000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'

# 2. Verify OTP (save the token)
TOKEN=$(curl -X POST http://localhost:8000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "otp": "1234", "name": "John"}' \
  | jq -r '.access_token')

# 3. Use token to access protected endpoint
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Request OTP
response = requests.post(f"{BASE_URL}/auth/request-otp", json={
    "phone": "+1234567890"
})
print(response.json())

# 2. Verify OTP
response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
    "phone": "+1234567890",
    "otp": "1234",
    "name": "John Doe"
})
data = response.json()
token = data["access_token"]

# 3. Access protected endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)
print(response.json())
```

### Using Swagger UI

1. Start the backend: `uvicorn backend.main:app --reload`
2. Visit: http://localhost:8000/docs
3. Try the endpoints:
   - POST `/auth/request-otp`
   - POST `/auth/verify-otp` (copy the token)
   - Click "Authorize" button at top
   - Enter: `Bearer <your-token>`
   - Try GET `/me`

---

## File Structure

```
backend/
├── config.py              # JWT & app configuration
├── deps.py                # Auth dependencies
├── utils/
│   └── auth.py           # JWT token utilities
├── routers/
│   └── auth.py           # Auth endpoints
└── main.py               # App with auth router
```

---

## Troubleshooting

### "Could not validate credentials"

- Token expired (check ACCESS_TOKEN_EXPIRE_MINUTES)
- Token malformed
- JWT_SECRET mismatch
- User deleted from database

### "Invalid OTP"

- OTP must be exactly "1234" in demo mode
- Check spelling and no extra spaces

### "Access denied. Customer role required"

- User role doesn't match required role
- Check user.role in database
- Admin can access admin-only routes

### "Not authenticated"

- Missing Authorization header
- Token not prefixed with "Bearer "
- Check header format: `Authorization: Bearer <token>`

---

## Next Steps

1. **Add refresh tokens** for better security
2. **Implement real OTP system** with SMS provider
3. **Add password option** as alternative auth
4. **Social login** (Google, Apple, etc.)
5. **Two-factor authentication** for admins
6. **Session management** (track active sessions)

**The authentication system is complete and ready to use! 🔐**

