# 🔧 Provider Flow Documentation

## Overview

Complete implementation of the provider journey from managing profile to completing jobs with status updates.

---

## Pages Implemented

### 1. Provider Home (`/provider/home`)

**Purpose:** Main dashboard for providers

**Features:**
- ✅ Display provider profile information
- ✅ Online/Offline toggle
- ✅ Update location button
- ✅ View nearby requests button
- ✅ View active jobs button
- ✅ Quick stats (total jobs, avg rating)

**Flow:**
1. Page loads and fetches provider profile
2. Provider can toggle online/offline status
3. Provider can update GPS location
4. Navigate to requests or jobs

**API Calls:**
```typescript
GET /provider/profile
PUT /provider/profile { is_online: true/false }
POST /provider/location { lat, lng }
```

---

### 2. Nearby Requests (`/provider/requests`)

**Purpose:** View and bid on nearby service requests

**Features:**
- ✅ Adjustable search radius (5-50 km slider)
- ✅ Request cards with distance
- ✅ Service and vehicle details
- ✅ Customer description
- ✅ Offer form per request
  - Custom price input
  - ETA input
  - "Accept Offered Price" button
  - "Send Counter-Offer" button
- ✅ Refresh button
- ✅ Sorted by distance

**Flow:**
1. Page loads nearby requests within radius
2. Provider sees request cards sorted by distance
3. Provider enters price and ETA
4. Clicks accept or counter-offer
5. Offer sent to customer
6. Request removed from list

**API Calls:**
```typescript
GET /provider/nearby-requests?radius_km=10
POST /provider/offers {
  service_request_id,
  price,
  eta_minutes
}
```

---

### 3. Active Jobs List (`/provider/jobs/active`)

**Purpose:** View all active jobs

**Features:**
- ✅ List of non-completed jobs
- ✅ Job cards with service details
- ✅ Price and status display
- ✅ Click to view job details
- ✅ Empty state with CTA

**Flow:**
1. Shows all jobs not completed/cancelled
2. Provider clicks on job card
3. Navigate to job detail page

**API Call:**
```typescript
GET /provider/jobs/active
```

---

### 4. Job Detail (`/provider/job/[jobId]`)

**Purpose:** Manage and update active job

**Features:**
- ✅ Job status display
- ✅ Service details
- ✅ Customer location map
- ✅ Status update buttons
  - On the Way
  - Arrived
  - In Progress
  - Completed
- ✅ Update location button
- ✅ Real-time polling (10 seconds)
- ✅ Completion confirmation

**Flow:**
1. View job details and customer location
2. Click "On the Way" when starting
3. Update location as traveling
4. Click "Arrived" when at location
5. Click "In Progress" when working
6. Click "Completed" when finished

**API Calls:**
```typescript
GET /provider/jobs/active (to find job)
PATCH /provider/jobs/{jobId}/status { status }
POST /provider/location { lat, lng }
```

---

## Complete Provider Journey

### 1. Provider Setup

```
/provider/home
↓ Click "Go Online"
↓ Click "Update My Location" (allow GPS)
↓ Location: 37.7749, -122.4194
```

### 2. Find Request

```
/provider/requests
↓ Adjust radius to 15 km
↓ See 3 nearby requests
↓ Closest: Flat Tire, 2.3 km away, $75
↓ Enter price: $65
↓ Enter ETA: 15 min
↓ Click "Send Counter-Offer"
↓ Success! Request removed from list
```

### 3. Customer Accepts

```
(Wait for customer to accept your offer)
↓ Notification (future feature)
```

### 4. Complete Job

```
/provider/jobs/active
↓ See 1 active job
↓ Click on job card
↓ /provider/job/1
↓ See customer location on map
↓ Click "On the Way"
↓ Drive to location
↓ Click "Update My Location" periodically
↓ Click "Arrived"
↓ Click "In Progress"
↓ Perform service
↓ Click "Completed"
↓ Success message shown
```

---

## Key Features

### Online/Offline Toggle

```typescript
// Updates provider_profile.is_online
await providerAPI.updateProfile({ is_online: !profile.is_online });
```

**Benefits:**
- Only online providers see requests
- Prevents unwanted notifications when offline
- Clear status indicator

### Location Tracking

```typescript
navigator.geolocation.getCurrentPosition((position) => {
  await providerAPI.updateLocation(
    position.coords.latitude,
    position.coords.longitude
  );
});
```

**Recommendations:**
- Update every 30-60 seconds when active
- Update before viewing nearby requests
- Update while on the way to customer

### Offer Pricing Strategy

**Default:** Match customer's offered price
**Custom:** Send counter-offer (usually lower to be competitive)

```typescript
// Auto-calculated defaults
price: request.price_offered  // Match customer
eta: Math.ceil(distance_km * 3)  // 3 minutes per km
```

### Status Progression

```
assigned → on_the_way → arrived → in_progress → completed
```

**Sequential buttons:**
- Can't skip steps
- Previous steps are disabled
- Current and next steps enabled

---

## Error Handling

### Location Not Set

```
Error: "Provider location not set. Please update your location first."
```

**Solution:** Click "Update My Location" on home page

### Already Sent Offer

```
Error: "You already have a pending offer on this request"
```

**Solution:** Wait for customer decision or find other requests

### Request No Longer Available

```
Error: "Service request is not accepting offers. Current status: offer_selected"
```

**Solution:** Request was already accepted by another provider

---

## Best Practices

### 1. Keep Location Updated

Update location every minute when online:

```typescript
useEffect(() => {
  if (profile?.is_online) {
    const interval = setInterval(() => {
      updateLocation();
    }, 60000);
    return () => clearInterval(interval);
  }
}, [profile]);
```

### 2. Competitive Pricing

Offer 10-20% less than customer's price:

```typescript
const competitivePrice = request.price_offered * 0.85;
```

### 3. Realistic ETA

Calculate based on distance and traffic:

```typescript
const eta = Math.ceil(distance_km * 3); // 3 min per km
// Add buffer for traffic/parking
const etaWithBuffer = eta + 5;
```

### 4. Quick Response

- Check nearby requests frequently
- Send offers quickly
- First offer has advantage

---

## Testing

### Test Scenario

```bash
# 1. Login as provider
http://localhost:3000/login
Phone: +2222222222
OTP: 1234

# 2. Set role to provider (if needed)
# In backend: UPDATE users SET role='provider' WHERE phone='+2222222222'

# 3. Test flow:
   - Go online
   - Update location
   - View nearby requests (need customer to create one)
   - Send offer
   - Check active jobs (after customer accepts)
   - Update job status
   - Complete job
```

---

## See Also

- `FRONTEND.md` - Frontend architecture
- `CUSTOMER_FLOW.md` - Customer pages
- `backend/PROVIDER_API.md` - Provider API documentation

**The provider flow is fully functional! 🔧**

