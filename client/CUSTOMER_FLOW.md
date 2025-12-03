# 🚗 Customer Flow Documentation

## Overview

Complete implementation of the customer journey from requesting help to job completion with real-time updates and location tracking.

---

## Pages Implemented

### 1. Customer Home (`/customer/home`)

**Purpose:** Main dashboard for customers

**Features:**
- ✅ Greeting with user name
- ✅ Automatic geolocation detection
- ✅ Location display with simple map
- ✅ "Need Roadside Help" CTA button
- ✅ How it works guide
- ✅ Location error handling

**Flow:**
1. Page loads and requests geolocation permission
2. Once location is detected, user can proceed
3. Click "Need Roadside Help" → Navigate to request form

---

### 2. Service Request Form (`/customer/request`)

**Purpose:** Create a new service request

**Features:**
- ✅ Service type dropdown (Flat Tire, Jump Start, Fuel, Tow, Lockout, Other)
- ✅ Vehicle type selection (Car/Bike)
- ✅ Optional description textarea
- ✅ Price input with validation
- ✅ Automatic location from context
- ✅ Manual location entry option
- ✅ Form validation
- ✅ Error handling

**Flow:**
1. Select service type and vehicle
2. Enter description (optional)
3. Set price
4. Location auto-filled or manually entered
5. Submit → Navigate to offers page

**API Call:**
```typescript
POST /customer/service-requests
{
  service_type: "flat_tyre",
  vehicle_type: "car",
  description: "Flat tire on Highway 101",
  price_offered: 75.0,
  lat: 37.7749,
  lng: -122.4194
}
```

---

### 3. Offers Page (`/customer/offers/[requestId]`)

**Purpose:** View and accept offers from providers

**Features:**
- ✅ Request summary display
- ✅ Real-time offer polling (every 5 seconds)
- ✅ Offer cards with provider info
- ✅ Provider rating and verification badges
- ✅ Price comparison
- ✅ ETA display
- ✅ Accept offer button
- ✅ Auto-redirect to job page when accepted
- ✅ Waiting state when no offers yet

**Flow:**
1. Page loads and fetches request details
2. Displays request summary
3. Polls for new offers every 5 seconds
4. Shows "Waiting for offers" if empty
5. User clicks "Accept" on an offer
6. Redirects to job tracking page

**API Calls:**
```typescript
// Polling
GET /customer/service-requests/{requestId}

// Accept offer
POST /customer/offers/{offerId}/accept
```

**Offer Card Display:**
- Provider name with verification badge
- Price with comparison to your offer
- ETA in minutes
- Rating stars
- Accept button

---

### 4. Job Tracking (`/customer/job/[jobId]`)

**Purpose:** Track active job with provider location

**Features:**
- ✅ Job status display with color-coded badges
- ✅ Real-time status polling (every 10 seconds)
- ✅ Service details summary
- ✅ Provider information with rating
- ✅ Map with customer and provider locations
- ✅ Status-specific messages
- ✅ Rating form when completed
- ✅ Auto-refresh indicator

**Job Statuses:**
- **Assigned** 📝 - Provider has been notified
- **On the Way** 🚗 - Provider is en route
- **Arrived** 📍 - Provider at location
- **In Progress** 🔧 - Service being performed
- **Completed** ✅ - Job finished
- **Cancelled** ❌ - Job cancelled

**Flow:**
1. Page loads and fetches job details
2. Displays status, service info, provider info
3. Shows map with both locations
4. Polls every 10 seconds for updates
5. When completed, shows rating form
6. User can request another service

**API Call:**
```typescript
// Polling
GET /customer/jobs/{jobId}
```

---

## Complete User Journey

### Happy Path Example

```
1. Customer lands on /customer/home
   ↓ [Location detected: 37.7749, -122.4194]
   ↓ [Clicks "Need Roadside Help"]

2. Customer on /customer/request
   ↓ [Selects "Flat Tire", "Car"]
   ↓ [Enters price: $75]
   ↓ [Clicks "Submit Request"]
   ↓ [API creates request #123]

3. Customer on /customer/offers/123
   ↓ [Polling shows "Waiting for offers..."]
   ↓ [5 seconds later: 0 offers]
   ↓ [10 seconds: 1 offer appears]
   ↓ [15 seconds: 2 offers total]
   ↓ [Customer reviews offers]
   ↓ [Clicks "Accept" on $65 offer]
   ↓ [API creates job #45]

4. Customer on /customer/job/45
   ↓ [Status: "assigned"]
   ↓ [10 seconds: status updates to "on_the_way"]
   ↓ [Provider location shows on map]
   ↓ [20 seconds: status "arrived"]
   ↓ [30 seconds: status "in_progress"]
   ↓ [Job completes]
   ↓ [Rating form appears]
   ↓ [Customer rates 5 stars]
```

---

## Location Context

### Implementation

```typescript
// context/LocationContext.tsx
interface Location {
  lat: number;
  lng: number;
}

// Shared across customer pages
const { location, setLocation } = useLocation();
```

### Usage

**Get Location:**
```typescript
navigator.geolocation.getCurrentPosition(
  (position) => {
    setLocation({
      lat: position.coords.latitude,
      lng: position.coords.longitude
    });
  },
  (error) => {
    console.error('Location error:', error);
  }
);
```

**Use in Forms:**
```typescript
const { location } = useLocation();

// Use in API call
await customerAPI.createServiceRequest({
  ...data,
  lat: location.lat,
  lng: location.lng
});
```

---

## Polling Implementation

### Offers Page (5-second polling)

```typescript
useEffect(() => {
  if (!request || request.job) return; // Stop if job exists

  const interval = setInterval(() => {
    fetchRequest(); // Refresh data
  }, 5000);

  return () => clearInterval(interval); // Cleanup
}, [request]);
```

### Job Page (10-second polling)

```typescript
useEffect(() => {
  // Don't poll if completed or cancelled
  if (!job || job.status === 'completed' || job.status === 'cancelled') {
    return;
  }

  const interval = setInterval(() => {
    fetchJob(); // Refresh data
  }, 10000);

  return () => clearInterval(interval);
}, [job]);
```

---

## Map Integration

### Simple Map Placeholder

Currently using a gradient background with markers:

```tsx
<div className="bg-gradient-to-br from-blue-100 to-green-100 rounded-lg h-64">
  {/* Customer Location */}
  <div>
    <div className="text-3xl">📍</div>
    <p>Your Location</p>
    <p>{lat}, {lng}</p>
  </div>

  {/* Provider Location */}
  {hasProviderLocation && (
    <div>
      <div className="text-3xl">🚗</div>
      <p>Provider Location</p>
      <p>{providerLat}, {providerLng}</p>
    </div>
  )}
</div>
```

### Future: Google Maps Integration

```bash
npm install @react-google-maps/api
```

```typescript
import { GoogleMap, Marker } from '@react-google-maps/api';

<GoogleMap
  center={{ lat: customerLat, lng: customerLng }}
  zoom={13}
>
  <Marker position={{ lat: customerLat, lng: customerLng }} />
  <Marker position={{ lat: providerLat, lng: providerLng }} />
</GoogleMap>
```

---

## Error Handling

### Location Errors

```typescript
if (!location && !useManualLocation) {
  setError('Location is required. Please enable location services.');
}
```

### API Errors

```typescript
try {
  const response = await customerAPI.createServiceRequest(data);
} catch (err: any) {
  setError(err.response?.data?.detail || 'Failed to create request');
}
```

### Not Found Errors

```typescript
if (error && !request) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      {error}
    </div>
  );
}
```

---

## Navigation Flow

```
/customer → redirects to → /customer/home
                              ↓
                       /customer/request
                              ↓
                  /customer/offers/[requestId]
                              ↓
                    /customer/job/[jobId]
                              ↓
                       /customer/home (new request)
```

---

## Testing the Flow

### Complete Test Scenario

```bash
# 1. Start backend
cd backend
uvicorn main:app --reload

# 2. Start frontend
cd client
npm run dev

# 3. Login as customer
http://localhost:3000/login
Phone: +1234567890
OTP: 1234

# 4. Should redirect to /customer/home
# 5. Allow location when prompted
# 6. Click "Need Roadside Help"
# 7. Fill form and submit
# 8. Watch offers appear (need provider to send offers)
# 9. Accept an offer
# 10. Track job status
```

### Test with Provider

Open two browser windows:
1. **Window 1:** Customer journey (above)
2. **Window 2:** Provider dashboard (send offers)

---

## Key Features

✅ **Geolocation** - Automatic location detection  
✅ **Real-time Updates** - Polling for offers and job status  
✅ **Form Validation** - Proper input validation  
✅ **Error Handling** - User-friendly error messages  
✅ **Loading States** - Spinners and indicators  
✅ **Mobile-First** - Responsive design  
✅ **Status Tracking** - Visual job status updates  
✅ **Provider Info** - Ratings and verification  
✅ **Map Display** - Simple location visualization  

---

## Next Enhancements

1. **Google Maps** - Interactive maps with directions
2. **Push Notifications** - Alert when offer received
3. **Payment Integration** - Process payments
4. **Request History** - View past requests
5. **Favorites** - Save favorite providers
6. **Chat** - Message provider during job
7. **Photos** - Upload problem photos
8. **Cancel Request** - Cancel before accepting offer

**The customer flow is fully functional and ready to use! 🚗**

