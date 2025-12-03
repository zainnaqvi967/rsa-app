# 📊 Admin Dashboard Documentation

## Overview

Complete admin dashboard for monitoring and managing the Roadside Assistance Marketplace system.

**Authentication Required:** Admin role

---

## Page: `/admin/dashboard`

### Features

✅ **Three Data Tables**
1. Active Service Requests
2. All Jobs
3. All Providers (with verification toggle)

✅ **Summary Stats Cards**
- Active requests count
- Total jobs count
- Total providers count

✅ **Provider Verification**
- Toggle verification status
- Real-time updates

✅ **Parallel Data Loading**
- Fetches all data at once
- Fast initial load

---

## Data Sections

### 1. Active Service Requests

**Filters:** Shows only `pending_offers` or `offer_selected` status

**Columns:**
- ID
- Customer name/ID
- Service type
- Vehicle type
- Price offered
- Number of offers
- Status (color-coded badge)
- Created date

**Color Coding:**
- Yellow badge = Pending offers
- Green badge = Offer selected

---

### 2. Jobs Table

**Shows:** All jobs in the system

**Columns:**
- Job ID
- Status (color-coded)
- Service type
- Customer name/ID
- Provider name/ID
- Created date
- Last updated date

**Status Colors:**
- Green = Completed
- Red = Cancelled
- Blue = Active (assigned, on_the_way, arrived, in_progress)

---

### 3. Providers Table

**Shows:** All provider profiles

**Columns:**
- Profile ID
- Name
- Phone
- City
- Services offered
- Status (online/offline)
- Rating with count
- **Verification toggle button**

**Verification Toggle:**
- Click to verify/unverify provider
- Updates immediately
- Green button = Verified
- Yellow button = Unverified

---

## API Calls

### On Page Load (Parallel)

```typescript
const [requestsRes, jobsRes, providersRes] = await Promise.all([
  adminAPI.getServiceRequests(),
  adminAPI.getJobs(),
  adminAPI.getProviders(),
]);
```

### Toggle Verification

```typescript
await adminAPI.updateProviderVerification(profileId, !isVerified);

// API: PATCH /admin/providers/{profileId}
// Body: { "is_verified": true/false }
```

---

## Testing

### Create Admin User

First, manually set a user to admin role in the database:

```bash
# Start backend
cd backend
uvicorn main:app --reload

# In another terminal, access SQLite
sqlite3 roadside_assistance.db

# Set user to admin
UPDATE users SET role = 'admin' WHERE phone = '+9999999999';
.exit
```

### Test Flow

```bash
# 1. Login as admin
http://localhost:3000/login
Phone: +9999999999
OTP: 1234

# 2. Should redirect to /admin/dashboard

# 3. View all data:
   - Active service requests
   - All jobs
   - All providers

# 4. Test verification toggle:
   - Click on unverified provider
   - Button changes to verified
   - Verify in backend: GET /admin/providers
```

---

## Example Admin Tasks

### Monitor System Activity

```typescript
// Check active requests
const activeRequests = requests.filter(r => 
  r.status === 'pending_offers' || r.status === 'offer_selected'
);
console.log(`${activeRequests.length} active requests`);

// Check completion rate
const completedJobs = jobs.filter(j => j.job_status === 'completed');
const completionRate = (completedJobs.length / jobs.length * 100).toFixed(1);
console.log(`Completion rate: ${completionRate}%`);

// Check verified providers
const verifiedProviders = providers.filter(p => p.is_verified);
console.log(`${verifiedProviders.length}/${providers.length} providers verified`);
```

### Identify Issues

```typescript
// Requests with no offers
const noOffers = requests.filter(r => 
  r.status === 'pending_offers' && r.offer_count === 0
);

// Stuck jobs
const stuckJobs = jobs.filter(j => {
  const hoursSinceUpdate = 
    (Date.now() - new Date(j.job_updated_at).getTime()) / (1000 * 60 * 60);
  return hoursSinceUpdate > 2 && j.job_status !== 'completed';
});

// Offline providers
const offlineProviders = providers.filter(p => !p.is_online);
```

---

## Styling

Clean, functional design with Tailwind CSS:

**Tables:**
- Zebra striping on hover
- Clear headers with uppercase labels
- Responsive overflow scrolling
- Color-coded status badges

**Cards:**
- White background with shadow
- Clear section headers
- Organized data presentation

**Stats:**
- Color-coded by category
- Large numbers for visibility
- Brief labels

---

## Future Enhancements

1. **Filters & Search**
   - Filter by date range
   - Search by customer/provider name
   - Status filters

2. **Pagination**
   - Paginate tables for large datasets
   - Show 25/50/100 per page

3. **Analytics Charts**
   - Request trends over time
   - Provider performance metrics
   - Revenue tracking

4. **Bulk Actions**
   - Verify multiple providers at once
   - Export data to CSV
   - Bulk notifications

5. **Real-time Updates**
   - WebSocket for live data
   - Auto-refresh tables
   - Desktop notifications

6. **Detailed Views**
   - Click row to see full details
   - Edit capabilities
   - Action history/audit log

---

## Security Note

**Admin users must be created manually:**

```sql
-- In SQLite database
UPDATE users SET role = 'admin' WHERE phone = '+1234567890';
```

For production, implement a secure admin registration system with master keys or invite codes.

---

## See Also

- `FRONTEND.md` - Frontend architecture
- `CUSTOMER_FLOW.md` - Customer pages
- `backend/ADMIN_API.md` - Admin API documentation

**The admin dashboard is fully functional! 📊**

