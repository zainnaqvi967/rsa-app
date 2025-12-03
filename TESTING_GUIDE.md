# 🧪 Complete Testing Guide

## Prerequisites

Make sure both backend and frontend are running:

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd client
npm install
npm run dev
```

---

## 📱 Demo Credentials

After running `python seed.py`, use these credentials:

| Role | Phone | Name | Details |
|------|-------|------|---------|
| **Customer** | `+923111234567` | Sara Khan | Ready to request help |
| **Provider** | `+923009876543` | Ali Mechanic | Online in Islamabad, verified |
| **Admin** | `+923001234567` | Admin User | Full system access |

**OTP for all users: `1234`**

---

## 🎯 Test Scenario 1: Complete Customer Journey

### Step 1: Login as Customer

1. Open http://localhost:3000
2. Click "Login / Continue"
3. Enter phone: `+923111234567`
4. Click "Send OTP"
5. Enter OTP: `1234`
6. Click "Verify"
7. ✅ Should redirect to `/customer/home`

### Step 2: Create Service Request

1. On customer home page, click "Allow" when browser asks for location
   - **Alternative:** Click "Enter Manually" and use: `33.6844, 73.0479`
2. Click "Need Roadside Help"
3. Fill the form:
   - Service Type: **Flat Tire**
   - Vehicle Type: **Car**
   - Description: "Front left tire is flat near F-7 Markaz"
   - Price Offered: **75**
4. Click "Submit Request"
5. ✅ Should redirect to `/customer/offers/[requestId]`

### Step 3: Wait for Offers

1. Page shows "We're notifying nearby helpers..."
2. Page polls every 5 seconds
3. Leave this browser window open
4. ⏳ Wait for provider to send offer

### Step 4: Accept Offer

1. After provider sends offer, it appears automatically
2. See offer details: Provider name, price, ETA, rating
3. Click "Accept This Offer"
4. ✅ Should redirect to `/customer/job/[jobId]`

### Step 5: Track Job

1. See job status badge (initially "Assigned")
2. See provider info and rating
3. See map with customer and provider locations
4. Watch status update as provider works:
   - **On the Way** → "Your helper is on the way!"
   - **Arrived** → "Your helper has arrived!"
   - **In Progress** → "Service in progress..."
   - **Completed** → Job complete message appears
5. Rate the service (1-5 stars)
6. ✅ Job completed successfully!

---

## 🔧 Test Scenario 2: Complete Provider Journey

### Step 1: Login as Provider (New Browser/Incognito)

1. Open http://localhost:3000 in **incognito/private window**
2. Click "Login / Continue"
3. Enter phone: `+923009876543`
4. Click "Send OTP"
5. Enter OTP: `1234`
6. Click "Verify"
7. ✅ Should redirect to `/provider/home`

### Step 2: Check Profile

1. See profile info:
   - Name: Ali Mechanic
   - City: Islamabad
   - Services: All types
   - Status: **Online** (green badge)
   - Rating: ⭐ 4.8 (24 reviews)
2. ✅ Already online from seed script

### Step 3: View Nearby Requests

1. Click "View Nearby Requests"
2. Adjust radius slider (try 10-50 km)
3. Click "Search Nearby Requests"
4. See customer's request from Scenario 1:
   - Service: Flat Tire
   - Vehicle: Car
   - Price: $75
   - Distance: ~0.1 km (same location)
   - Description shown

### Step 4: Send Offer

1. For the flat tire request, see offer form:
   - Price input (pre-filled with $75)
   - ETA input (pre-filled with estimated time)
2. **Option A:** Click "Accept at Offered Price" ($75)
3. **Option B:** Enter custom price ($65) and click "Send Counter-Offer"
4. ✅ Success message: "Offer sent successfully!"
5. Request disappears from list

### Step 5: Wait for Customer to Accept

1. Click "View My Active Jobs" in header
2. Initially shows "No active jobs"
3. Wait for customer to accept (go to customer browser)
4. After customer accepts, job appears automatically
5. Click on the job card

### Step 6: Complete the Job

1. On job detail page, see:
   - Customer location on map
   - Service details
   - Current status: **Assigned**
2. Click "On the Way"
   - ✅ Status updates to "On the Way"
   - Customer sees update
3. **(Optional)** Click "Update My Location"
4. Click "Arrived"
   - ✅ Status updates to "Arrived"
5. Click "In Progress"
   - ✅ Status updates to "In Progress"
6. Click "Completed"
   - ✅ Status updates to "Completed"
   - Success message shown
7. ✅ Job completed successfully!

---

## 👑 Test Scenario 3: Admin Dashboard

### Step 1: Login as Admin

1. Open http://localhost:3000 in **another browser/window**
2. Click "Login / Continue"
3. Enter phone: `+923001234567`
4. Click "Send OTP"
5. Enter OTP: `1234`
6. Click "Verify"
7. ✅ Should redirect to `/admin/dashboard`

### Step 2: View Dashboard

1. See summary stats at top:
   - **Active Requests:** Count of pending/offer_selected
   - **Total Jobs:** Count of all jobs
   - **Providers:** Count of all providers
2. ✅ Numbers reflect system state

### Step 3: View Active Service Requests

1. Scroll to "Active Service Requests" table
2. See customer's request (if still pending)
3. View details:
   - ID, Customer, Service, Vehicle, Price, Offers, Status, Created
4. ✅ All data displayed correctly

### Step 4: View Jobs

1. Scroll to "Jobs" table
2. See all jobs in system
3. View details:
   - Job ID, Status, Service, Customer, Provider, Created, Updated
4. Status badges color-coded:
   - Green = Completed
   - Red = Cancelled
   - Blue = Active
5. ✅ Job from test scenario visible

### Step 5: Manage Providers

1. Scroll to "Providers" table
2. See Ali Mechanic listed:
   - Online status: Green badge
   - Rating: ⭐ 4.8 (24)
   - Verification: Green "✓ Verified" button
3. Click verification button
4. ✅ Changes to "⚠ Unverified" (yellow)
5. Click again
6. ✅ Changes back to "✓ Verified" (green)

### Step 6: Refresh Data

1. Click "🔄 Refresh Data" button at bottom
2. ✅ All tables reload with latest data

---

## 🔄 Test Scenario 4: Real-time Updates

### Setup: Three Browsers Side-by-Side

- **Browser 1:** Customer at `/customer/job/[jobId]`
- **Browser 2:** Provider at `/provider/job/[jobId]`
- **Browser 3:** Admin at `/admin/dashboard`

### Test Real-time Polling

1. **Provider** clicks "Arrived"
2. Within 10 seconds, **Customer** sees status update to "Arrived"
3. **Admin** clicks refresh, sees updated job status
4. ✅ All views stay synchronized

---

## 🧪 Test Scenario 5: Multiple Offers

### Setup

1. Login as customer, create a service request
2. Login as **first provider** (seeded), send offer
3. Create **second provider**:
   - Login with new phone (e.g., `+923005555555`)
   - Will be created as customer by default
   - Change role in database:
     ```sql
     sqlite3 roadside_assistance.db
     UPDATE users SET role='provider' WHERE phone='+923005555555';
     ```
   - Login again
4. Update location and send offer on same request

### Expected Results

1. Customer sees **two offers** on offers page
2. Customer can accept either offer
3. After accepting one:
   - That offer status → "accepted"
   - Other offer status → "rejected"
   - Service request status → "offer_selected"
   - New job created
4. ✅ Only accepted offer creates a job

---

## ⚠️ Error Scenarios to Test

### 1. Location Not Available

**Test:**
- Block location in browser
- Go to `/customer/request`
- Try to submit without enabling manual entry

**Expected:**
- Error message: "Location is required..."
- Form doesn't submit

### 2. Invalid OTP

**Test:**
- Enter phone, request OTP
- Enter wrong OTP (e.g., `0000`)

**Expected:**
- Error message: "Invalid OTP"
- Stays on OTP step

### 3. Wrong Role Access

**Test:**
- Login as customer
- Manually navigate to `/provider/home`

**Expected:**
- Automatically redirected to `/login`

### 4. No Active Requests

**Test:**
- Login as provider
- Click "View Nearby Requests" with no requests nearby

**Expected:**
- Message: "No nearby requests found"
- Suggestion to adjust radius

### 5. Request Already Has Offer Selected

**Test:**
- Customer accepts an offer
- Provider tries to send another offer on same request

**Expected:**
- API returns error: "Service request is not accepting offers"
- Error displayed to provider

---

## ✅ Success Criteria

After running all scenarios, verify:

- [x] Customer can request help and track jobs
- [x] Provider can see requests and send offers
- [x] Multiple offers work correctly
- [x] Job status updates flow through system
- [x] Admin can view all data
- [x] Admin can toggle provider verification
- [x] Real-time polling works (5s and 10s intervals)
- [x] Location detection works
- [x] Manual location entry works
- [x] Error messages are clear and helpful
- [x] Role-based redirects work
- [x] Token authentication persists across refreshes
- [x] Logout clears data and redirects to home

---

## 🐛 Known Limitations (MVP)

1. **OTP is hardcoded** to `1234` for demo
2. **Polling instead of WebSocket** - 5-10 second delays
3. **Maps are placeholders** - show coordinates, not interactive maps
4. **No photo upload** for service requests
5. **No chat system** between customer and provider
6. **No push notifications** - users must keep browser open
7. **SQLite database** - not production-ready at scale
8. **No rate limiting** on API endpoints
9. **No email notifications**
10. **No payment integration**

These are **intentional for MVP** and documented in roadmap.

---

## 📊 Database Inspection

To inspect the database during testing:

```bash
cd backend
sqlite3 roadside_assistance.db

# View all users
SELECT * FROM users;

# View service requests
SELECT id, customer_id, service_type, status, created_at FROM service_requests;

# View offers
SELECT id, service_request_id, provider_id, price, status FROM offers;

# View jobs
SELECT id, service_request_id, status, created_at FROM jobs;

# Exit
.exit
```

---

## 🔧 Troubleshooting

### Backend not starting
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed (Windows)
taskkill /PID <process_id> /F

# Restart
uvicorn main:app --reload
```

### Frontend not starting
```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database issues
```bash
# Delete and reseed
rm roadside_assistance.db
python seed.py
```

### Token issues
- Clear browser localStorage
- F12 → Application → Local Storage → Clear All
- Login again

---

## 🎉 Testing Complete!

If all scenarios pass, your MVP is **production-ready**! 🚀

**Next steps:**
1. Deploy to production
2. Test with real users
3. Collect feedback
4. Iterate on features

